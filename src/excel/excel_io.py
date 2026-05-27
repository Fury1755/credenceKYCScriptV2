'''
This module handles downloading and uploading of excel workbooks.
'''

from playwright.sync_api import Page
from openpyxl import Workbook
from helper_functions import log_rate_limit
import io
import os
import openpyxl
import logging

def download_excel(page: Page, site_url: str, excel_relative_path: str) -> Workbook:
    '''downloads the Excel file'''
    endpoint = f"{site_url}/_api/web/GetFileByServerRelativeUrl('{excel_relative_path}')/$value"
    response = page.request.get(endpoint)

    if response.ok:
        excel_bytes = response.body()  # loads the bytes of the object into RAM
        excel_buffer = io.BytesIO(excel_bytes)  # wraps the bytes in a file
        wb = openpyxl.load_workbook(excel_buffer)  # load it into a workbook
        logging.info("Workbook downloaded")
        log_rate_limit(response)

        return wb

    error_msg = "Download failed: %s - %s", response.status, response.text()[:200]
    logging.error("Download failed: %s - %s", response.status, response.text()[:200])
    raise RuntimeError(error_msg)

def get_request_digest(page: Page, site_url: str) -> str:
    '''
    Sharepoint requires a valid X-RequestDigest header for state-changing operations like
    POST, PUT and DELETE.
    '''

    #sends a request to fetch context info from the endpoint
    response = page.request.post(f"{site_url}/_api/contextinfo",
                                 # force the response the be in json, otherwise returns XML
                                 headers={
                                     "Accept": "application/json;odata=verbose"
                                 })

    if not response.ok:  # response.ok returns a bool
        error_msg = "Get digest failed: %s - %s", response.status, response.text()
        logging.error(error_msg)
        raise RuntimeError(error_msg)

    log_rate_limit(response)
    data = response.json()  # returns parsed json

    # go through bunch of arrays to get the digest
    digest = data["d"]["GetContextWebInformation"]["FormDigestValue"]
    return digest

def workbook_to_bytes(wb: Workbook) -> bytes:
    '''Converts openpyxl workbook to bytes'''
    buffer = io.BytesIO()  # initialize/declare an object made of raw bytes
    wb.save(buffer)  # save workbook to buffer
    return buffer.getvalue()


def upload_excel(page: Page, wb: Workbook,  site_url: str, excel_relative_path: str):
    '''Uploads an openpyxl Workbook to the url provided'''

    # first process the path name
    folder = os.path.dirname(excel_relative_path)
    filename = os.path.basename(excel_relative_path)

    digest = get_request_digest(page, site_url)
    wb_bytes = workbook_to_bytes(wb)
    api_url = (
        f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{folder}')"
        f"/Files/add(url='{filename}', overwrite=true)"  # overwrite=true preserves versioning
    )

    response = page.request.post(
        # the new file name is based off the decoded url parameter
        url=api_url,
        headers={
            "Accept": "application/json;odata=verbose",
            "X-RequestDigest": digest,

            # specify the MIME type to be safe
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
        data=wb_bytes
    )

    if not response.ok:
        error_msg = "Upload failed: %s - %s", response.status, response.text()
        logging.error("Upload failed: %s - %s", response.status, response.text())
        raise RuntimeError(error_msg)

    log_rate_limit(response)
    logging.info("Workbook uploaded")
