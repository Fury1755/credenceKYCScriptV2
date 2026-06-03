"""This module defines private folder methods for the class SharePointClient."""

from playwright.sync_api import APIResponse, Page
from boundary.sharepoint_exceptions import (
    SharePointAttributeError,
    SharePointContractViolation,
    SharePointDuplicateError,
    SharePointKeyError,
)

from core import string_helpers
from typing import Optional, List
from abc import abstractmethod
import logging

# pylint: disable=protected-access
# ^^ makes everything private which is what we want


class FolderMixin:
    """mixin for sharepoint_client's folder functions"""

    @property
    # abstract methods are just fancy forward declarations.
    @abstractmethod
    def page(self) -> Page:
        """
        The Page object is a reference to the live, mutable Page.
        By extension this property is mutable.
        """

    @property
    @abstractmethod
    def file_system_object_type(self) -> int:
        """Returns the 'FileSystemObjectType' property as an integer."""

    @property
    @abstractmethod
    def site_url(self) -> str:
        """The site URL."""

    @property
    @abstractmethod
    def server_relative_url(self) -> str:
        """Returns the ServerRelativeUrl of a SharePoint list item."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the 'Name' property."""

    @property
    @abstractmethod
    def time_last_modified(self) -> str:
        """Returns the TimeLastModified property."""

    @abstractmethod
    def _request(self, method: str, url: str, **kwargs) -> APIResponse: ...

    # We make walk_folder a private method so that it doesn't leak APIResponse to anything outside
    def _walk_folder(self) -> APIResponse:
        """
        This function returns an APIResponse from the current client. The caller
        client must be a folder.
        """

        # precondition check: the caller must be a folder
        if self.file_system_object_type != 1:  # 1 is the value for folders
            logging.error("SharePoint object %s is not a folder", self.name)
            raise SharePointContractViolation(
                "Passed a non-folder object to walk_folder"
            )

        # this is in odata syntax
        # first line is the site_url
        endpoint = (
            f"{self.site_url}/_api/web/"  # '/' is a path separator
            # select folder
            # In this script, URLs are passed around unencoded
            f"GetFolderByServerRelativeUrl('{self.server_relative_url}')"
            # include child folders and files
            # '?' marks the start of query parameters
            # '$' marks odata system query parameters
            "?$expand=Folders,Files"
            # specify root folder fields, so the response includes itself (the root folder)
            #  and we know where the children came from
            # '&' separates query parameters when thhere is more than one
            "&$select=Folders,Files,Name,ServerRelativeUrl,TimeLastModified,FileSystemObjectType,"
            # filter child fields
            "Folders/Name,Folders/ServerRelativeUrl,"
            "Folders/TimeLastModified,Folders/FileSystemObjectType,"
            "Files/Name,Files/ServerRelativeUrl,Files/TimeLastModified,Files/FileSystemObjectType"
        )

        logging.debug("Endpoint: %s", endpoint)
        response = self._request(
            "GET", endpoint, headers={"Accept": "application/json;odata=verbose"}
        )

        return response

    def _unwrap_response(
        self, response: APIResponse
    ) -> dict[str, dict[str, List[dict[str, str]]]]:
        """Unwraps 'd' from the APIResponse's json"""

        # defensive programming habit: load once: Multiple reads are performance intensive
        #  and fragile
        response_json = response.json()

        # check if the "d" wrapper exists. It's inconsistent across SharePoint responses.
        if "d" in response_json:
            response_data = response_json["d"]
            logging.debug("Key 'd' found in response '%s'", self.name)
        else:
            response_data = response_json
            logging.debug("No key 'd' in response '%s'", self.name)

        return response_data

    def _get_folders(
        self, response_data: dict[str, dict[str, List[dict[str, str]]]]
    ) -> Optional[List[dict[str, str]]]:
        """Returns a List 'Folders' from an unwrapped response"""
        # provide empty Dicts and Lists to default to if nothing is found;
        #  enables more flexible custom error handling.
        # Otherwise, KeyError will be thrown instead (which is what happened in config.py)
        # We assume results will exist because we always request with application;odata=verbose
        folders = response_data.get("Folders", {}).get("results", [])
        return folders

    def _get_files(
        self, response_data: dict[str, dict[str, List[dict[str, str]]]]
    ) -> Optional[List[dict[str, str]]]:
        """Returns a List 'Files' from an unwrapped response"""
        files = response_data.get("Files", {}).get("results", [])
        return files

    def _get_item_data(
        self, query: str, items: Optional[List[dict[str, str]]]
    ) -> Optional[dict[str, str]]:
        """Returns the an item with a key 'Name' matching the query.
        Takes a list of dictionaries as arguments."""
        if not items:
            return None
        item_names: List[str] = [item["Name"] for item in items]
        name = string_helpers.best_match_item(query, item_names)
        for item in items:
            if item["Name"] == name:
                return item
        logging.error("Query %s not found in %s", query, self.name)
        raise SharePointKeyError(f"Query {query} not found in client '{self.name}'.")

    def _get_folders_and_files(
        self, response: APIResponse
    ) -> Optional[dict[str, List[dict[str, str]]]]:
        """Returns a dictionary of 'Files' and 'Folders' from a SharePoint response."""

        response_data = self._unwrap_response(response)

        output = {}

        # provide empty Dicts and Lists to default to if nothing is found;
        #  enables more flexible custom error handling.
        # Otherwise, KeyError will be thrown instead (which is what happened in config.py)
        # We assume results will exist because we always request with application;odata=verbose
        folders = self._get_folders(response_data)
        files = self._get_files(response_data)

        if files:
            output["Files"] = files
        if folders:
            output["Folders"] = folders

        if not output:
            # We don't raise an error; let the caller handle the None
            logging.debug("Output from get_folders_and_files '%s' is None", self.name)

        return output

    def _decide_folder(self, query: str) -> str:
        """
        Takes the response of a folder directory
        and returns a server relative id_value corresponding to a item whose
        name is closest to the matching query.
        """

        response = self._walk_folder()
        results = self._get_folders_and_files(response)

        if results is not None:
            if "Folders" in results:
                folders = results["Folders"]
            else:
                raise SharePointContractViolation(
                    f"Attempted to access non-existing 'Folders' objects in {self.name}"
                )
        else:
            raise SharePointContractViolation(
                f"Attempted to access non-existing folders and files in '{self.name}'"
            )

        # According to the REST API, calling with $expand guarantees wrapping in ['results']
        name_list = [item["Name"] for item in folders]
        match = string_helpers.best_match_item(query, name_list)

        # this *should* return a List with a single item.
        # Nevertheless, we guard against it.
        match_item = [item for item in folders if item["Name"] == match]

        if len(match_item) != 1:
            logging.error(
                "Expected 1 match in folder '%s', got %d matches to the query string. "
                "\nQuery: %s",
                self.name,
                len(match_item),
                query,
            )
            raise SharePointDuplicateError(
                f"More than one item found in {str(response.json())[:100]} \nQuery: {match}"
            )

        return match_item[0]["ServerRelativeUrl"]

    def _parse_item_type(self, item_data: dict) -> int:
        """Takes a SharePoint item's item_data as input and returns its type"""
        if "FileSystemObjectType" in item_data:
            return int(item_data["FileSystemObjectType"])
        if "__metadata" in item_data:
            item_metadata = item_data["__metadata"]
            item_type = item_metadata.get("type", {}).lower()
            if "folder" in item_type:
                logging.debug("Found object with type 'Folder'")
                return 1
            if "web" in item_type:
                # because we don't expect to find web
                logging.warning("Found object with type 'Web'")
                return 2
            if "file" in item_type:
                logging.debug("Found object with type 'File'")
                return 0
            if "invalid" in item_type:
                logging.warning("Accessing invalid item in %s", self.name)
                return -1

        logging.error("Type attribute not accessed in %s", self.name)
        raise SharePointAttributeError("Error: Type attribute not accessed")

    def _compare_pdfs(
        self, file: dict[str, str], most_recent_file: dict[str, str]
    ) -> bool:
        if not (".pdf" in file["Name"].lower() and "profile" in file["Name"].lower()):
            return False
        # ISO formats for date times are lexicographically comparable
        if file["TimeLastModified"] >= most_recent_file["TimeLastModified"]:
            logging.info(
                "Updated TimeLastModified to %s", file["TimeLastModified"]
            )
            return True
        return False


