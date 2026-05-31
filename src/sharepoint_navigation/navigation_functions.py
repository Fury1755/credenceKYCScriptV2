"""
This module contains functions that navigate sharepoint folders.
"""

from playwright.sync_api import Page, APIResponse
from helpers import response_helpers, string_helpers
from typing import List
import re
import logging


def walk_folders(page: Page, endpoint_id: str, site_url: str) -> APIResponse:
    """
    This function gets the subfolders and files of a folder's relative URL.
    """

    # this is in odata syntax
    # first line is the site_url
    endpoint = (
        f"{site_url}/_api/web/"  # '/' is a path separator
        # select folder
        f"GetFolderByServerRelativeUrl('{endpoint_id}')"
        # include child folders and files
        # '?' marks the start of query parameters
        # '$' marks odata system query parameters
        "?$expand=Folders,Files"
        # specify root folder fields, so the response includes itself (the root folder)
        #  and we know where the children came from
        # '&' separates query parameters when thhere is more than one
        "&$select=Name,ServerRelativeUrl,"
        # filter child fields
        "Folders/Name,Folders/ServerRelativeUrl,"
        "Files/Name,Files/ServerRelativeUrl"
    )

    response = response_helpers.request_with_retry(
        page, "GET", endpoint, headers={"Accept": "application/json;odata=verbose"}
    )

    return response


def get_folders_and_files(response: APIResponse) -> dict[str, List[dict[str, str]]]:
    """Returns a dictionary of 'Files' and 'Folders' from a Sharepoint response."""
    response_data = response.json()["d"]
    output = {}

    # provide empty Dicts and Lists to default to if nothing is found
    # more flexible custom error handling
    folders = response_data.get("Folders", {}).get("results", [])

    files = response_data.get("Files", {}).get("results", {})

    if files:
        output["Files"] = files
    if folders:
        output["Folders"] = folders

    if not output:
        logging.error("No folders or files found in response %s", response.text())
        raise RuntimeError("get_folders_and_files found no folders or files")
    return output


def get_folder_and_file_names(response: APIResponse) -> dict[str, List[str]]:
    """Returns a dictionary of 'Folders' and 'Files' names from a Sharepoint response."""

    # According to the REST API, calling with $expand guarantees wrapping in ['results']
    # And any item is guaranteed to have a property 'Name'
    results = get_folders_and_files(response)
    name_list = {}
    if results.get("Files", {}):
        name_list["Files"] = [item["Name"] for item in results["Files"]]
    if results.get("Folders", {}):
        name_list["Folders"] = [item["Name"] for item in results["Folders"]]

    # We don't need error checking; get_folders_and_files would have caught it already.
    return name_list

def get_folder_names(response: APIResponse) -> List[str]:
    '''Returns a List of 'Folders' names from a Sharepoint response.'''

    output = get_folder_and_file_names(response).get("Folders")

    if not output:
        logging.error("get_folder_names found no folders in %s", response.text())
        raise RuntimeError("get_folder_names found no Folders")
    
    return output


def decide_folder(response: APIResponse, query: str) -> str:
    """
    Takes the response of a folder directory
    and returns a server relative id corresponding to a item whose
    name is closest to the matching query.
    """

    # According to the REST API, calling with $expand guarantees wrapping in ['results']
    results = get_folders_and_files(response).get("Folders", {})
    if not results:
        logging.error("%s does not contain any folders", response.text())
        raise RuntimeError("No folder passed to decide_folder")
    name_list = [item["Name"] for item in results]
    match = string_helpers.best_match_item(query, name_list)

    # this *should* return a List with a single item.
    # Nevertheless, we guard against it.
    match_item = [item for item in results if item["Name"] == match]

    if len(match_item) != 1:
        logging.error(
            "Expected 1 match, got %d. response_data: %s \nQuery: %s",
            len(match_item),
            str((response.json())[:100]),
            match,
        )
        raise RuntimeError(
            f"More than one item found in {str(response.json())[:100]} \nQuery: {match}"
        )

    return match_item[0]["ServerRelativeUrl"]


def bizfile_collector(company_response: APIResponse):
    """Recursively iterates through and gets the most recent ACRA bizfile in a company."""

    acradocs_id = decide_folder(company_response, "ACRA Docs")
    response = company_response

    # Recursive block below
    
    contents = get_folders_and_files(response)
    folders = contents.get("Folders", {})
    files = contents.get("Files", {})

    #  Let's get all the profile pdfs first
    if files:
        # We know files exists in this block but we use | None to satisfy type checker
        file_names: List[str] | None = get_folder_and_file_names(response).get("Files")
        profile_names = []
        if file_names:  # again, type checker
            for name in file_names:
                if name.lower() == re.compile(r".*profile.*") and name.endswith(".pdf"):
                    profile_names.append(name)
