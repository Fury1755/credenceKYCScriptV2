"""This module orchestrates sharepoint functions, and is called by main.py"""
# Obviously, functions defined here are not generic and specific to this sharepoint site only.

from sharepoint_navigation.navigation_functions import (
    walk_folders,
    decide_folder,
    get_folder_names,
)
from playwright.sync_api import Page, APIResponse
from helpers.url_helpers import get_url_id
from helpers import string_helpers


def get_latest_company(
    page: Page,
    site_url: str,
    company_list_by_letter_path: str,
    current_letter: str,
    prev_company: str,
) -> APIResponse:
    """Returns the APIResponse of the latest company's folder."""
    list_id: str = get_url_id(company_list_by_letter_path)
    company_list_response: APIResponse = walk_folders(page, list_id, site_url)
    letter_id: str = decide_folder(company_list_response, current_letter)
    letter_response = walk_folders(page, letter_id, site_url)
    letter_names = get_folder_names(letter_response)
    company_name = string_helpers.get_next_name(prev_company, letter_names)
    company_id = decide_folder(letter_response, company_name)
    company_response = walk_folders(page, company_id, site_url)
    return company_response
