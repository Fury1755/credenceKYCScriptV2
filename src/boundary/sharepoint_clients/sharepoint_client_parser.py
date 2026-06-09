"""
This module contains the class SharePointClientParser,
responsible for pure functions and logic within a SharePointClient
instance.
"""

from typing import List
import logging


class SharePointClientParser:
    """
    This class is a composition of SharePointClient. It handles
    pure functions and is trusted code.
    """

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
