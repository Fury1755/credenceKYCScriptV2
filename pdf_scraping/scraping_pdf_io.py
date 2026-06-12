"""
This module uses functions from src/boundary/pdf_io
to download PDFs to a specified directory in config.
"""

# hack to import src
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import logging
import os

from playwright.sync_api import Page

from src.boundary.pdf_io import download_pdf


def download_pdf_to_disk(
    page: Page,
    site_url: str,
    bizfile: dict[str, str],
    folder_path: str,
):
    """
    This function downloads a pdf to a local folder.

    Args:
        page: Playwright page object
        site_url: SharePoint site url
        bizfile: Dictionary with keys 'Name' and 'ServerRelativeUrl'
        folder_path: Destination directory, specified in config.py
    """

    download_path = os.path.join(folder_path, bizfile["Name"])
    pdf_buffer = download_pdf(page, site_url, bizfile)
    open(download_path, "wb").write(pdf_buffer.getvalue())
    logging.info("Downloaded '%s", bizfile["Name"])
