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
)
from boundary import response_helpers
from core import string_helpers
from boundary.sharepoint_client_helpers.folder_mixin import FolderMixin
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

    def _request(self, method: str, url: str, **kwargs) -> APIResponse:
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

    def get_next_company_name(
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
            previous_company[0].upper()  #  gets first letter of query as current letter
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

        current_letter_response = current_letter_list._walk_folder()
        current_letter_contents = current_letter_list._get_folders_and_files(
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
            current_company_relative = current_company_data["ServerRelativeUrl"]
            current_company_name = current_company_data["Name"]
            current_company_time = current_company_data["TimeLastModified"]
            current_company_type = current_company_data["FileSystemObjectType"]
            current_company = SharePointClient(
                self.page,
                self.site_url,
                current_company_relative,
                current_company_name,
                current_company_time,
                current_company_type,
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
