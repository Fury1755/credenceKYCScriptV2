"""
This module handles downloading and uploading of excel workbooks.
"""

from playwright.sync_api import Page
from openpyxl import Workbook
from helpers.response_helpers import get_request_digest, request_with_retry
import io
import os
import openpyxl
import logging


def download_excel(page: Page, site_url: str, relative_url: str) -> Workbook:
    """downloads the Excel file"""
    endpoint = (
        f"{site_url}/_api/web/GetFileByServerRelativeUrl('{relative_url}')/$value"
    )
    response = request_with_retry(
        page,
        "GET",
        endpoint,
        headers={"Accept": "application/json;odata=verbose"},
        max_retries=4,
    )
    if response.ok:
        excel_bytes = response.body()  # loads the bytes of the object into RAM
        excel_buffer = io.BytesIO(excel_bytes)  # wraps the bytes in a file
        wb = openpyxl.load_workbook(excel_buffer)  # load it into a workbook
        logging.info("Workbook downloaded")

        return wb

    logging.error("Download failed: %s - %s", response.status, response.text()[:200])
    raise RuntimeError(f"Download failed: {response.status} - {response.text()}")


def workbook_to_bytes(wb: Workbook) -> bytes:
    """Converts openpyxl workbook to bytes"""
    buffer = io.BytesIO()  # initialize/declare an object made of raw bytes
    wb.save(buffer)  # save workbook to buffer
    return buffer.getvalue()


def upload_excel(page: Page, wb: Workbook, site_url: str, relative_url: str):
    """Uploads an openpyxl Workbook to the url provided"""

    # first process the path name
    folder = os.path.dirname(relative_url)
    filename = os.path.basename(relative_url)

    digest = get_request_digest(page, site_url)
    wb_bytes = workbook_to_bytes(wb)
    api_url = (
        f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{folder}')"
        f"/Files/add(url='{filename}', overwrite=true)"  # overwrite=true preserves versioning
    )

    response = request_with_retry(
        page,
        "PUT",
        # the new file name is based off the decoded url parameter
        url=api_url,
        headers={
            "Accept": "application/json;odata=verbose",
            "X-RequestDigest": digest,
            # specify the MIME type to be safe
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
        data=wb_bytes,
    )

    if (
        not response.ok
    ):  # we already have checks in response but these are unique to the function
        logging.error("Upload failed: %s - %s", response.status, response.text())
        raise RuntimeError(f"Upload failed: {response.status} - {response.text()}")

    logging.info("Workbook uploaded")
