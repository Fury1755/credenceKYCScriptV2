"""
This is the main module. It it initialises the browser instance and orchestrates functions.
This script uses playwright's page.get() to send requests to SharePoint's REST API.
I tried to make the functions as pure as possible for max reliability
"""

#from playwright.sync_api import sync_playwright
from cloakbrowser import launch_persistent_context
import config
from core import url_helpers
from boundary import search
from boundary.excel_io import download_excel
from core.excel_processing import get_latest_company_name
from orchestration.sharepoint_orchestration import get_current_company
from orchestration.pdf_orchestration import get_individuals

import logging
import time

logging.basicConfig(
    level=logging.INFO,
    # Notice how the below parameters don't use f-strings
    # Logging's format string is stored once, then the placeholders are
    #  replaced by specific values from the specific log record (mutable
    #  template applied to different data)
    # Whereas f-strings are created immediately at the time of
    #  execution (immutable string at runtime)
    format="%(asctime)s - %(levelno)s - %(funcName)s - %(message)s",
    # A handler determines where the log goes.
    # For this script, StreamHandler is sufficient (writes to console)
    handlers=[logging.StreamHandler()],
)


context = launch_persistent_context(
    user_data_dir=config.BROWSER_PROFILE_DIR,
    channel="msedge",
    headless=False,
    args=[
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1920,1080",
        "--force-device-scale-factor=1.5",
        "--window-position=1,1",
        "--start-maximized",
    ],
    viewport={"width": 1280, "height": 720},
)

page = (
    context.pages[0] if context.pages else context.new_page()
)  # grab the page object
for p in context.pages[1:]:  # close irrelevant pages
    p.close()

# process excel url
excel_id = url_helpers.get_excel_relative_url(config.EXCEL_URL)

# refresh the cookies
page.goto(config.SITE_URL)

wb = download_excel(page, config.SITE_URL, excel_id)

latest_company_name = get_latest_company_name(wb, config.CURRENT_LETTER)

current_company = get_current_company(
    page, config.SITE_URL, config.COMPANY_LIST_BY_LETTER_PATH, latest_company_name
)

bizfile = current_company.get_bizfile(current_company)

kah_list = get_individuals(page, config.SITE_URL, bizfile)
print(kah_list)

screenshots = search.search_master(page, kah_list)
print(screenshots)


try: #error handling; if it hits an error in the try block then it defaults to except:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    time.sleep(0.1)
    print("Script terminated")

#  don't need context.close(); playwright closes it automatically at the end of 'with'
