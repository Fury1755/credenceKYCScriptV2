'''
This is the main module. It it initialises the browser instance and orchestrates functions.
This script uses playwright's page.get() to send requests to Sharepoint's REST API.
The functions are written to be as pure as possible.
'''
from playwright.sync_api import sync_playwright
from config import BROWSER_PROFILE_DIR, SITE_URL, CURRENT_LETTER, EXCEL_RELATIVE_PATH
from excel.excel_io import download_excel, upload_excel
from excel.excel_processing import read_latest_company

with sync_playwright() as pw:
    context = pw.chromium.launch_persistent_context(
        user_data_dir=BROWSER_PROFILE_DIR,
        channel='msedge',
        headless=False,
        args=[
            '--no-first-run',
            '--no-default-browser-check',
            '--window-size=1920,1080',
            '--force-device-scale-factor=1.5',
            '--window-position=0,0',
            '--start-maximized'
            ],
        viewport={'width':1280,'height':720}
    )

    page = context.pages[0] if context.pages else context.new_page() #grab the page object
    for p in context.pages[1:]: #close irrelevant pages
        p.close()

    page.goto(SITE_URL) #refresh the cookies

    wb = download_excel(page=page, site_url=SITE_URL, excel_relative_path=EXCEL_RELATIVE_PATH)
    wb = read_latest_company(wb=wb, CURRENT_LETTER=CURRENT_LETTER)
    upload_excel(page=page, wb=wb, site_url=SITE_URL, excel_relative_path=EXCEL_RELATIVE_PATH)
    #  don't need context.close(); playwright closes it automatically at the end of 'with'
