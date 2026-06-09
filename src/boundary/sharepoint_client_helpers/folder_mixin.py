"""This module defines private folder methods for the class SharePointClient."""

from playwright.sync_api import APIResponse, Page
from boundary.sharepoint_exceptions import (
    SharePointAttributeError,
    SharePointContractViolation,
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
    def request(self, method: str, url: str, **kwargs) -> APIResponse:
        """Wrapper around request_with_retry encapsulated in client."""

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
        response = self.request(
            "GET", endpoint, headers={"Accept": "application/json;odata=verbose"}
        )

        return response

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
        """Returns an item with a key 'Name' matching the query.
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
            logging.info("Updated TimeLastModified to %s", file["TimeLastModified"])
            return True
        return False
