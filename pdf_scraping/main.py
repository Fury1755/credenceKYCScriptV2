"""
This module utilizes existing logic from src to scrape the SharePoint site for
PDFs, used to unit test 'process_pdf' in 'pdf_processing.py'.
"""

# hack to import config
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # project root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))  # src directory


from cloakbrowser import launch_persistent_context
from src import config
from src.core.url_helpers import get_url_id
from scraping_pdf_io import download_pdf_to_disk
from boundary.sharepoint_clients.sharepoint_client import SharePointClient

import logging


# set up and configure, same as main
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelno)s - %(funcName)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


context = launch_persistent_context(
    user_data_dir=config.BROWSER_PROFILE_DIR,
    # channel="msedge",
    headless=True,
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

page = context.pages[0] if context.pages else context.new_page()
for p in context.pages[1:]:
    page.close()

page.goto(config.SITE_URL)

a_to_z_list = SharePointClient(
    page,
    config.SITE_URL,
    get_url_id(config.COMPANY_LIST_BY_LETTER_PATH),
    "a_to_z_list",
    "dont matter",
    "1",
)

letter_list = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]

# pylint: disable=protected-access

a_to_z_response = a_to_z_list._walk_folder()

a_to_z_folders = a_to_z_list._get_folders(
    a_to_z_list._parser.unwrap_response(a_to_z_response)
)

if a_to_z_folders is None:
    raise RuntimeError("Could not locate folders of the directory that holds A to Z")

letter_array = [folder["Name"] for folder in a_to_z_folders]

for current_letter in letter_list:
    try:
        current_letter_id = a_to_z_list._decide_folder(current_letter)
        current_letter_client = SharePointClient(
            page, config.SITE_URL, current_letter_id, current_letter, "idk", "1"
        )

        current_letter_folders = current_letter_client.return_folders()
        if current_letter_folders is None:
            raise RuntimeError(f"No folders found in {current_letter}")

        company_name_list = [
            company_folder.name for company_folder in current_letter_folders
        ]
        prev_company = company_name_list[0]
        for company_client in current_letter_folders:
            try:
                bizfile = company_client.get_bizfile(company_client)
                download_pdf_to_disk(
                    page, config.SITE_URL, bizfile, config.PDF_TESTING_PATH
                )
            except Exception:  # pylint: disable=[W0718]
                logging.info(
                    "Could not get bizfile for %s. Continuing.", company_client.name
                )
                continue
    except Exception:  # pylint: disable=[W0718]
        logging.info(
            "Catastrophic failure occured in letter %s. Continuing to next letter:",
            current_letter,
        )
        continue
