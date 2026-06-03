"""This module handles the downloading of pdfs."""

import io
from boundary import response_helpers
from playwright.sync_api import Page, APIResponse


def pdf_to_bytes(response: APIResponse):
    '''Returns an in-memory pdf from a response'''

    pdf_bytes = response.body()
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0) # read pointer to the beginning
    return buffer

def download_pdf(page: Page, site_url, file_item: dict[str, str]):
    '''Downloads a pdf into memory'''

    endpoint = (f"{site_url}/_api/web/GetFileByServerRelativeUrl"
                f"('{file_item['ServerRelativeUrl']}')/$value")
    response = response_helpers.request_with_retry(
        page,
        "GET",
        endpoint,
        headers={"Accept":"application/json;odata=verbose"}
    )

    return pdf_to_bytes(response)
