'''
This is the main module. It it initialises the browser instance and orchestrates functions.
This script uses playwright's page.get() to send requests to Sharepoint's REST API.
I tried to make the functions as pure as possible for maximum reliability
'''

from playwright.sync_api import sync_playwright, APIResponse, Page
import config
from excel.excel_io import download_excel
from excel.excel_processing import get_latest_company_name
from sharepoint_navigation.navigation_functions import walk_folders, decide_folder, get_folder_names
from sharepoint_navigation import navigation_functions
from helpers import url_helpers, string_helpers
import logging

logging.basicConfig(
    level = logging.INFO,

    # Notice how the below parameters don't use f-strings
    # Logging's format string is stored once, then the placeholders are
    #  replaced by specific values from the specific log record (mutable
    #  template applied to different data)
    # Whereas f-strings are created immediately at the time of
    #  execution (immutable string at runtime)
    format = "%(asctime)s - %(levelno)s - %(funcName)s - %(message)s",

    # A handler determines where the log goes.
    # For this script, StreamHandler is sufficient (writes to console)
    handlers = [logging.StreamHandler()]
)

def get_company_response(page: Page,
                  last_company_name: str,
                  current_letter: str,
                  company_list_by_letter_url: str,
                  site_url: str) -> APIResponse:
    '''Takes input and returns the response of the next company folder.'''

    a_to_z: APIResponse = walk_folders(page,
                                        url_helpers.get_url_id(company_list_by_letter_url),
                                        site_url)
    letter_id: str = decide_folder(a_to_z, current_letter)
    single_letter: APIResponse = walk_folders(page, letter_id, site_url)
    name_list = get_folder_names(single_letter)
    next_name = string_helpers.get_next_name(last_company_name, name_list)
    company_id = decide_folder(single_letter, next_name)
    response = walk_folders(page,
                                    company_id,
                                    site_url)
    return response

with sync_playwright() as pw:
    context = pw.chromium.launch_persistent_context(
        user_data_dir=config.BROWSER_PROFILE_DIR,
        channel='msedge',
        headless=False,
        args=[
            '--no-first-run',
            '--no-default-browser-check',
            '--window-size=1920,1080',
            '--force-device-scale-factor=1.5',
            '--window-position=0,0',
            '--start-maximized',
            '--headless=new'
            ],
        viewport={'width':1280,'height':720}
    )

    browser_page = context.pages[0] if context.pages else context.new_page()  # type: ignore
    for p in context.pages[1:]: #close irrelevant pages
        p.close()

    # refresh the cookies
    browser_page.goto(config.SITE_URL)
    logging.info("Entered site url: %s", config.SITE_URL)

    wb = download_excel(browser_page, config.SITE_URL, config.EXCEL_RELATIVE_PATH)

    latest_company_name = get_latest_company_name(wb, config.CURRENT_LETTER)

    company_response = get_company_response(browser_page, latest_company_name,
                                            config.CURRENT_LETTER,
                                            config.COMPANY_LIST_BY_LETTER_URL,
                                            config.SITE_URL)
    print(navigation_functions.get_folder_names(company_response))




    #  don't need context.close(); playwright closes it automatically at the end of 'with'
