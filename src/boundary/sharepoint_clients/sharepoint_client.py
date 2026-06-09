"""
This module contains the class 'SharePointClient' that holds all attributes
and methods for a SharePoint object.
"""

# This is a working example of OOP and encapsulation.
# We achieve better modularization by putting API-related methods and objects
#  within a single class.
# That is the definition of a class; bundling data ('attributes') and behaviour
#  ('methods') together.

# We encapsulate ALL 'APIResponse's in here, anything outside this class should not see
#  APIResponse at all.

from playwright.sync_api import Page, APIResponse
from boundary.sharepoint_exceptions import (
    SharePointResponseError,
    SharePointError,
    SharePointKeyError,
    SharePointOverwriteError,
)
from boundary import response_helpers
from core import string_helpers
from boundary.sharepoint_client_helpers.folder_mixin import FolderMixin
from typing import Optional, List
import logging


class SharePointClient(FolderMixin):
    """
    All API requests are bundled in this client.
    An instance of this client is either a file, folder, web or error.
    """

    # __init__ is the name for a constructor
    # self refers to itself (that specific instance of the class)
    def __init__(
        self,
        page: Page,
        site_url: str,
        server_relative_url: str,
        name: str,
        time_last_modified: str,
        file_system_object_type: str,
    ):
        # stores the page argument as its attribute
        # we add an underscore before names to make them private
        self._page = page  # simultaneously initializes page as an attribute of itself
        self._site_url = site_url
        self._server_relative_url = server_relative_url
        self._name = name
        self._time_last_modified = time_last_modified
        self._file_system_object_type = file_system_object_type

    # We introduce a decorator '@'.
    # A decorator is just a way of shortening functions for the sake
    #  of syntax and semantic meaning.

    @property
    def server_relative_url(self) -> str:
        """Returns the ServerRelativeUrl of a SharePoint list item."""
        return self._server_relative_url

    # let's say we have an instance called "Client"
    # Instead of calling Client.RelativeServerUrl(Client), we can now do
    #  Client.RelativeServerUrl instead which looks like we are accessing the attribute
    # Of course we are actually calling a method that accesses the attribute
    # But @property makes a read method look like an attribute access which is clearer

    @property
    def page(self) -> Page:
        """
        The Page object is a reference to the live, mutable Page.
        By extension this property is mutable.
        """
        return self._page

    @property
    def site_url(self) -> str:
        """The site URL."""
        return self._site_url

    @property
    def name(self) -> str:
        """Returns the 'Name' property."""
        return self._name

    @property
    def time_last_modified(self) -> str:  # wow this is boring
        """Returns the TimeLastModified property."""
        return self._time_last_modified

    # By writing methods to get a class' attributes, we can rewrite the methods here
    #  to alter this class' behaviour globally, rather than going around and rewriting
    #  lines that access attributes directly.

    @property
    def file_system_object_type(self) -> int:
        """Returns the 'FileSystemObjectType' property as an integer."""
        # We convert to an integer value for clarity
        return int(self._file_system_object_type)

    def request(self, method: str, url: str, **kwargs) -> APIResponse:
        """
        Encapsulated request_with_retry method for a client instance.
        """

        # populates kwargs with headers dict
        headers = kwargs.pop("headers", {})

        # nicer way of setting if "Accept" not in headers then...
        headers.setdefault("Accept", "application/json;odata=verbose")
        try:
            response = response_helpers.request_with_retry(
                self.page, method, url, headers, **kwargs
            )
        except Exception as e:
            raise SharePointResponseError(e) from e  # 'from e' chains the traceback
        return response

    def _build_client_query(self, query: str) -> "SharePointClient":
        """Builds a SharePointClient with a name closest to the query."""

        response = self._walk_folder()
        contents = self._get_folders_and_files(response)
        if not contents:
            raise SharePointKeyError(
                f"Build client found no folders or files in {self.name}"
            )
        folder = None
        file = None
        folders = None
        files = None
        # get the best matching folder and file
        try:
            files = contents.get("Files", [])
            file = self._get_item_data(query, files)
        except (SharePointKeyError, ValueError):
            logging.info("No file '%s' in '%s'. Looking for folders:", query, self.name)

        try:
            folders = contents.get("Folders", [])
            folder = self._get_item_data(query, folders)
            logging.info("Found folder '%s' in %s.", query, self.name)
        except (SharePointKeyError, ValueError):
            logging.info("No folder '%s' in '%s'", query, self.name)

        item = None

        # select the best matching item to build the client with
        if folder and file:
            item_name = string_helpers.best_match_item(
                query, [folder["Name"], file["Name"]]
            )
            if folder["Name"] == item_name:
                item = folder
            else:
                item = file
        if not file:
            item = folder
        if not folder:
            item = file

        if item is None:
            logging.error(
                "Build client failed, no folders and files were found matching %s in %s",
                query,
                self.name,
            )
            raise SharePointError("Factory method '_build_client' failed")

        client = SharePointClient(
            self.page,
            self.site_url,
            item["ServerRelativeUrl"],
            item["Name"],
            item["TimeLastModified"],
            # I don't know if item is the correct type. If it works then it is.
            str(self._parse_item_type(item)),
        )

        return client

    def get_bizfile(self, company: "SharePointClient"):
        """Returns the name and time of the most recent bizfile"""

        # pylint: disable=protected-access
        acra_docs = company._build_client_query("ACRA Docs")
        acra_docs_response = acra_docs._walk_folder()
        acra_docs_contents = acra_docs._get_folders_and_files(acra_docs_response)
        if acra_docs_contents is None:
            raise SharePointError(f"No files and folders found in {acra_docs.name}")
        bizfile = acra_docs._bizfile_recursive_explorer(acra_docs_contents, None)
        if bizfile is None:
            raise SharePointError(f"Found no bizfiles at all in {company.name}")
        return bizfile

    def get_next_company(
        self, previous_company: str
    ) -> "SharePointClient":  # this is a public method
        """
        Returns the next company's folder as a SharePointClient instance.
        Takes the URL of the company list from [A-Z] ('Credence Advisory - Corp Sec')
        as input.
        """

        current_letter = previous_company[0].upper()
        logging.info("Current letter found: '%s'", current_letter)
        current_letter_relative = self._decide_folder(
            #  gets first letter of query as current letter
            current_letter,
        )
        current_letter_list = SharePointClient(
            # instantiates a single letter folder such as 'B' as a client
            self.page,
            self.site_url,
            current_letter_relative,  # the only thing that matters in this client instance
            current_letter,
            self.time_last_modified,  #  inaccurate, doesn't matter
            str(1),  # we know this is a folder
        )

        current_letter_response = current_letter_list._walk_folder()  # pylint: disable=protected-access
        current_letter_contents = current_letter_list._get_folders_and_files(  # pylint: disable=protected-access
            current_letter_response
        )

        company_names = []
        if current_letter_contents:
            try:
                folders = current_letter_contents["Folders"]
                if folders:
                    try:
                        company_names = [item["Name"] for item in folders]
                    except Exception as e:
                        logging.error(
                            "No property 'Name' found in the following items:"
                            "%s\nFolder name '%s':\n Derived from previous company name '%s'",
                            [item for item in folders],
                            current_letter,
                            previous_company,
                        )
                        raise SharePointKeyError(
                            f"'Folders' in '{current_letter_list.name}'"
                            "has no attribute 'Name'"
                        ) from e
            except Exception as e:
                logging.error(
                    "Current letter folder %s contains no folders", current_letter
                )
                raise SharePointKeyError(
                    f"Current letter folder '{current_letter}' "
                    "does not contain any folders."
                ) from e

        current_company_name = string_helpers.get_next_name(
            previous_company, company_names
        )
        current_company_data = self._get_item_data(
            current_company_name,
            self._get_folders(self._unwrap_response(current_letter_response)),
        )

        if not current_company_data:
            raise SharePointError(
                f"get_item_data on current company {current_company_name} returned nothing"
            )

        try:
            current_company = current_letter_list._build_client_query(  # pylint:disable=protected-access
                current_company_name
            )
            return current_company

        except Exception as e:
            logging.error(
                "Could not find required client attributes in object %s."
                "\n Previous folder name: %s",
                current_company_name,
                current_letter_list.name,
            )
            raise SharePointKeyError(
                f"Could not find item attributes in object {current_company_name}"
            ) from e

    def _bizfile_recursive_explorer(
        self,
        contents: dict[str, List[dict[str, str]]],
        most_recent_file: Optional[dict[str, str]],
    ) -> dict[str, str] | None:

        # pylint: disable=protected-access
        # returns a dictionary of the pdf containing all its attributes
        folders = contents.get("Folders")
        files = contents.get("Files")

        if files:
            for file in files:
                if not most_recent_file:
                    if (
                        file["Name"].lower().endswith(".pdf")
                        and "profile" in file["Name"].lower()
                    ):
                        most_recent_file = file
                else:
                    if self._compare_pdfs(file, most_recent_file):
                        # most_recent_file is changed to file
                        # this is fine because python doesnt pass by reference
                        # it is passed by a copy of reference
                        # so most_recent_file outside of this function does not mutate.
                        logging.debug(
                            "Found file '%s' with TimeLastModified '%s'",
                            file["Name"],
                            file["TimeLastModified"],
                        )
                        most_recent_file = file

        if folders:
            for folder in folders:
                logging.info("Entering folder '%s' in '%s'", folder["Name"], self.name)
                folder_client = SharePointClient(
                    self.page,
                    self.site_url,
                    folder["ServerRelativeUrl"],
                    folder["Name"],
                    folder["TimeLastModified"],
                    str(self._parse_item_type(folder)),
                )
                folder_contents = folder_client._get_folders_and_files(
                    folder_client._walk_folder()
                )
                if folder_contents:
                    most_recent_file = folder_client._bizfile_recursive_explorer(
                        folder_contents, most_recent_file
                    )

        return most_recent_file

    def create_folder(self, folder_name: str) -> "SharePointClient":
        """Creates a folder inside the client."""

        # pylint: disable=protected-access

        request_digest = response_helpers.get_request_digest(self.page, self.site_url)
        endpoint = (
            f"{self.site_url}/_api/web/GetFolderByServerRelativeUrl"
            f"('{self.server_relative_url}')"
            f"/Folders/add('{folder_name}')"
        )

        self_response = self._walk_folder()
        self_data = self._unwrap_response(self_response)
        # oh my god thank goodness this works
        # note to self: REWRITE THIS PLS
        self_folders = self._get_folders(self_data)
        if self_folders is None:
            logging.error(
                "Somehow, some way, create_folder found an existing folder in"
                " a newly created folder. Before "
                "anything was added to it. This should never happen."
            )
            raise SharePointError
        for folder in self_folders:
            if folder_name in folder:
                logging.error(
                    "Folder '%s' already exists in %s. Please delete manually - "
                    "this script is not authorized to delete items from sharepoint.",
                    folder_name,
                    self.name,
                )
                raise SharePointOverwriteError()

        response = self.request(
            "POST",
            endpoint,
            headers={
                "Accept": "application/json;odata=verbose",
                "X-RequestDigest": request_digest,
            },
        )

        if response.ok:
            logging.info("Created folder %s in %s", folder_name, self.name)
        elif response.status == 409:
            logging.error(
                "Object %s already exists in %s. Please delete manually - "
                "this script is not authorized to delete items from sharepoint.",
                folder_name,
                self.name,
            )
            raise SharePointOverwriteError()
        else:
            logging.error(
                "Attempt to create folder '%s' in %s failed. \n Response status text: %s",
                folder_name,
                self.name,
                response.status_text,
            )
            raise SharePointResponseError(
                f"Attempt to create folder '{folder_name}' in {self.name} failed"
            )

        folder_self = self._build_client_query(folder_name)

        return folder_self
