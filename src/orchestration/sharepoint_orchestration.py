"""This module glues boundary SharePoint functions and core logic."""

# Obviously, functions defined here are not generic and specific to this SharePoint site only.

from playwright.sync_api import Page
from boundary.sharepoint_client import SharePointClient
from boundary.sharepoint_exceptions import SharePointError, SharePointKeyError
from core.url_helpers import get_url_id
from urllib.parse import quote
import logging


def get_current_company(
    page: Page, site_url: str, server_raw_url: str, previous_company: str
) -> SharePointClient:
    """
    Returns a SharePointClient instance of the current company.
    Takes relative URLs from the Corp Sec [A-Z] directory as arguments.
    """

    server_relative_url = get_url_id(server_raw_url)

    a_to_z_list = SharePointClient(
        page,
        site_url,
        server_relative_url,
        "a to z placeholder name",
        "i dont care",
        "1",
    )

    current_company = a_to_z_list.get_next_company(previous_company)
    logging.info(
        "Successfully got next company '%s' as SharePointClient", current_company.name
    )

    return current_company


def go_to_sentroweb(sentroweb_client: "SharePointClient"):
    """Goes to the sentroweb_client's browser URL"""

    # pylint: disable=protected-access
    try:
        page = sentroweb_client.page
        endpoint = (
            f"{sentroweb_client.site_url}/Shared Documents/Forms/AllItems.aspx"
            f"?id={quote(sentroweb_client.server_relative_url)}"
        )
        page.goto(endpoint)
    except (SharePointError, SharePointKeyError):
        logging.warning(
            "Could not find 'Sentroweb Search' in %s. Navigating to company folder instead.",
            sentroweb_client.name,
        )
        company_endpoint = (
            # note: self.site_url is not standardized. change this later
            f"{sentroweb_client.site_url}/Shared Documents/Forms/AllItems.aspx"
            f"?id={quote(sentroweb_client.server_relative_url)}"
        )
        page = sentroweb_client.page
        page.goto(company_endpoint)
