"""
This is the main module. It it initialises the browser instance and orchestrates functions.
This script uses playwright's page.get() to send requests to SharePoint's REST API.
I tried to make the functions as pure as possible for max reliability
"""

# from playwright.sync_api import sync_playwright
import asyncio
import logging

import nest_asyncio
from cloakbrowser import launch_persistent_context

import config
from boundary.excel.excel_io import download_excel, upload_excel
from boundary.excel.excel_processing import append_excel, get_latest_company_name
from boundary.pdf_io import create_pdf_folders, upload_pdfs
from boundary.search_new.search_orchestrator import search_orchestrator
from orchestration.pdf_orchestration import get_individuals
from orchestration.sharepoint_orchestration import (
    get_current_company,
    go_to_sentroweb,
)

nest_asyncio.apply()

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
    # channel="msedge",
    headless=False,
    args=[
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1920,1080",
        "--window-position=1,1",
        "--start-maximized",
    ],
    viewport={"width": 1280, "height": 720},
    device_scale_factor=2,
)

page = context.pages[0] if context.pages else context.new_page()  # grab the page object
for p in context.pages[1:]:  # close irrelevant pages
    p.close()

# refresh the cookies
page.goto(config.SITE_URL, timeout=60000)

while True:
    wb = download_excel(page, config.SITE_URL, config.EXCEL_URL)

    latest_company_name = get_latest_company_name(wb, config.CURRENT_LETTER)

    current_company = get_current_company(
        page,
        config.SITE_URL,
        config.COMPANY_LIST_BY_LETTER_PATH,
        latest_company_name,
        config.CURRENT_LETTER,
    )

    bizfile = current_company.get_bizfile(current_company)

    kah_list = get_individuals(page, config.SITE_URL, bizfile)

    sentroweb_client = current_company._build_client_query("Sentroweb Search")  # pylint: disable=protected-access

    go_to_sentroweb(sentroweb_client)

    screenshots, kah_list = asyncio.run(search_orchestrator(kah_list))

    for kah in kah_list:
        print(f"{kah.name} - {kah.role}")

    pdf_folders = create_pdf_folders(config.CURRENT_YEAR, sentroweb_client, kah_list)

    upload_pdfs(pdf_folders, screenshots)

    wb = download_excel(page, config.SITE_URL, config.EXCEL_URL)

    wb = append_excel(wb, config.CURRENT_LETTER, kah_list, current_company)

    upload_excel(page, wb, config.SITE_URL, config.EXCEL_URL)

#  don't need context.close(); playwright closes it automatically at the end of 'with'
