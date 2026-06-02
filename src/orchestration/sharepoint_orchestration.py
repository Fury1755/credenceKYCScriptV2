"""This module glues boundary SharePoint functions and core logic."""

# Obviously, functions defined here are not generic and specific to this SharePoint site only.

from playwright.sync_api import Page
from boundary.sharepoint_client import SharePointClient
from core.url_helpers import get_url_id


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

    current_company = a_to_z_list.get_next_company_name(previous_company)
    return current_company
