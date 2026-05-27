'''
This module finds the succeeding company after the one that has already been KYC-ed
'''

from playwright.sync_api import Page
import logging
import helper_functions
from sharepoint_types import SharePointFolder
from helper_functions import log_rate_limit
from typing import List

def get_company_list(
        page: Page,
        company_list_by_letter_path: str,
        site_url: str
        ) -> List[SharePointFolder]:
    '''
    This function goes to the endpoint with the companies sorted
     in alphabetical folder directories.

    Returns a List of dicts
    '''

    # get the endpoint id from the raw URL
    endpoint_id = helper_functions.get_url_id(company_list_by_letter_path)

    # now we build our url
    # NO TRAILING SLASH!!! Use GetFolder instead of GetFile!!!
    endpoint = (f"{site_url}/_api/web/GetFolderByServerRelativeUrl"
                f"('{endpoint_id}')/Folders")  # cuh we gotta stop forgetting parentheses

    response = page.request.get(
            endpoint,
            # we pass a dictionary to the headers parameter, 'Accept' is the key
            # the value is a HTTP header value
            # we want json because it's easier to work with in python; json becomes a native dict
            headers={"Accept": "application/json;odata=verbose"}
            )

    if response.ok:
        logging.info("Entered the company list at %s", endpoint)
        log_rate_limit(response)
    else:
        error_msg = ("Could not get endpoint from %s: - %s - %s",
                      endpoint, response.status, response.text())
        logging.error("Could not get endpoint from %s: - %s - %s",
                      endpoint, response.status, response.text())
        raise RuntimeError(error_msg)

    response_data = response.json()

    #folder_list is a list of folder objects
    folder_list = response_data['d']['results']

    return folder_list


