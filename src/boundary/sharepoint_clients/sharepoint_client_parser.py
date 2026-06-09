"""
This module contains the class SharePointClientParser,
responsible for pure functions and logic within a SharePointClient
instance.
"""

from playwright.sync_api import APIResponse
from typing import List, Optional
import logging


class SharePointClientParser:
    """
    This class is a composition of SharePointClient. It handles
    pure functions and is trusted code.
    """

    def unwrap_response(
        self, response: APIResponse
    ) -> dict[str, dict[str, List[dict[str, str]]]]:
        """Unwraps 'd' from the APIResponse's json"""

        # defensive programming habit: load once: Multiple reads are performance intensive
        #  and fragile
        response_json = response.json()

        # check if the "d" wrapper exists. It's inconsistent across SharePoint responses.
        if "d" in response_json:
            response_data = response_json["d"]
        else:
            response_data = response_json

        return response_data

    def get_folders_and_files(
        self, response: APIResponse
    ) -> Optional[dict[str, List[dict[str, str]]]]:
        """Returns a dictionary of 'Files' and 'Folders' from a SharePoint response."""

        response_data = self.unwrap_response(response)

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

        return output

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

    def get_folder_names_from_contents(
        self,
        contents: dict[str, List[dict[str, str]]] | None,
    ) -> List[str]:
        """
        Returns folder names from contents.

        Args:
            contents (dict): A parsed JSON response from SharePoint's
                `_get_folders_and_files` (the unwrapped 'd' object)

        Returns:
            List[str]: A list of folder names.

        Raises:
            KeyError: if the 'Folders' or 'Name' key(s) is/are missing.
            ValueError: if the argument passed is falsy.

        """

        # precondition: contents must be true
        if not contents:
            logging.error("Empty dict/none passed to _get_folder_names_from_contents")
            raise ValueError

        # precondition: 'Folders' must exist
        folders = contents.get("Folders", {})
        if not folders:
            logging.error("Could not find 'Folders' in %s", contents)
            raise KeyError("Expected key 'Folders' in dict")

        folder_names = []

        # precondition: 'Name' must exist in every instance of 'Folders'
        for folder in folders:
            folder_name = folder.get("Name", {})
            if not folder_name:
                logging.error("Folder %s has no key 'Name'", folder)
                raise KeyError("Could not find 'Name' in folder object")
            folder_names.append(folder_name)

        return folder_names
