"""This module handles the downloading of pdfs."""

import io
from boundary.sharepoint_clients.sharepoint_client import SharePointClient
from core.individual import Individual
from boundary.response_helpers import get_request_digest, request_with_retry
from boundary.sharepoint_exceptions import SharePointResponseError
from playwright.sync_api import Page, APIResponse
from typing import List
import logging


def pdf_to_bytes(response: APIResponse):
    """Returns an in-memory pdf from a response"""

    pdf_bytes = response.body()
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)  # read pointer to the beginning
    return buffer


def download_pdf(page: Page, site_url: str, file_item: dict[str, str]):
    """Downloads a pdf into memory"""

    endpoint = (
        f"{site_url}/_api/web/GetFileByServerRelativeUrl"
        f"('{file_item['ServerRelativeUrl']}')/$value"
    )
    response = request_with_retry(
        page, "GET", endpoint, headers={"Accept": "application/json;odata=verbose"}
    )

    if not response.ok:
        logging.error(
            "Response: %s - %s - %s",
            response.status,
            response.text(),
            endpoint,
        )
        raise SharePointResponseError(
            f"PDF download failed - response: {response.status}"
        )
    return pdf_to_bytes(response)


def create_pdf_folders(
    current_year: str,
    sentroweb_client: SharePointClient,
    individual_list: List[Individual],
) -> dict[Individual, SharePointClient]:
    """Creates the appropriate folder structures in the sentroweb folder client,
    returns a dictionary of individuals and their corresponding pdf files to be uploaded to."""

    # create the folder for the year
    year_client = sentroweb_client.create_folder(current_year)

    # create the folder for each individual
    individual_folders: dict[Individual, SharePointClient] = {}
    for individual in individual_list:
        individual_folder = year_client.create_folder(individual.name)
        individual_folders[individual] = individual_folder

    search_folders: dict[Individual, SharePointClient] = {}

    for individual, individual_folder in individual_folders.items():
        if individual.baidu is False:
            search_folder = individual_folder.create_folder("Google")
        else:
            search_folder = individual_folder.create_folder("Google and Baidu")

        search_folders[individual] = search_folder

    return search_folders


def upload_pdfs(
    search_folders: dict[Individual, SharePointClient],
    screenshots: List[dict[str, dict[str, bytes]]],
):
    """Uploads pdfs to the folders"""

    for individual, folder in search_folders.items():
        file_dict = None
        for screenshot in screenshots:
            if f"{individual.name}" in screenshot:
                file_dict = screenshot[f"{individual.name}"]

        if file_dict is None:
            # This should never happen; I don't think this will ever happen.
            raise RuntimeError(
                "Individual name not found in argument provided for 'screenshots'"
            )
        for file_name, data in file_dict.items():
            post_pdf({file_name: data}, folder)


def post_pdf(file_dict: dict[str, bytes], folder: SharePointClient):
    """posts a single pdf to the folder"""
    digest = get_request_digest(folder.page, folder.site_url)
    endpoint = (
        f"{folder.site_url}"
        f"/_api/web/GetFolderByServerRelativeUrl('{folder.server_relative_url}')"
        # next(iter()) accesses key value in a dict
        f"/Files/add(url='{next(iter(file_dict))}.png', overwrite=true)"
    )

    response = folder.request(
        "POST",
        # the new file name is based off the decoded url parameter
        url=endpoint,
        headers={
            "Accept": "application/json;odata=verbose",
            "X-RequestDigest": digest,
            "Content-Type": "image/png",
        },
        data=next(iter(file_dict.values())),  # accesses the value in file_dict
    )

    if not response.ok:
        logging.error("PDF upload response status: \n%s", response.status_text)
        raise SharePointResponseError(f"PDF uploading failed: status {response.status}")
    logging.info("File '%s' uploaded to %s", next(iter(file_dict)), folder.name)
