"""This module contains generic helper functions that interact directly with server responses."""

from playwright.sync_api import APIResponse, Page
from typing import Optional
import logging
import time

# for extract_retry_after
from email.utils import parsedate_to_datetime  # for HTTP/RFC 2822 dates and asctime
from datetime import timezone, datetime


def log_rate_limit(response: APIResponse):
    """
    Logs warnings when rate limit headers are found.
    """

    headers: dict[str, str] = response.headers
    rate_limit_dict: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower().startswith("ratelimit"):
            rate_limit_dict[key] = value

    if rate_limit_dict:  # yes, you can check for empty dicts this way
        logging.warning("Rate limit detected: ")
        for key, value in rate_limit_dict.items():
            logging.warning("%s - %s", key, value)


def extract_retry_after(response: APIResponse) -> Optional[float]:
    """
    Returns time before next retry, if any, in seconds.
    Returns None if no header 'Retry-After' found or date not parsed.
    """

    # note to self:
    # every function should have an explicit return (even if that value is None)
    #  or return nothing at all.

    retry_after = response.headers.get("Retry-After")
    if not retry_after:
        return None
    if retry_after.isdigit():  # returns true if all char are digits
        return float(retry_after)

    # We are not done! Servers can return Retry-After values in
    #  two different styles: a simple number <delay-seconds> which
    #  parses as an integer, or a timestamp <http-date> which looks like
    #  a combination of date and time. We have to account for the second.

    try:
        # returns a datetime object. Can be naive or aware (contains timezone info)
        reset_time = parsedate_to_datetime(retry_after)

        # instead of trying to figure out which timezone, we force all timezones to be UTC.
        now = datetime.now(timezone.utc)

        # Find total seconds to wait

        wait_time = (reset_time - now).total_seconds()
        return wait_time

    except (TypeError, ValueError, OverflowError):
        logging.warning("No date parsed in %s", response.headers)
        return None


def request_with_retry(
    page: Page,
    method: str,
    url: str,
    headers: dict[str, str],
    max_retries: int = 5,
    # Keyword arguments let you pass parameters of any type.
    # Used to account for the possible parameters included in page.request,
    #  such as requesting for data or bytes for our excel sheet.
    **kwargs,
) -> APIResponse:
    """
    Sends generic requests from a page with built-in rate throttling; Exponential backoff
    if no Retry-After is found.
    """

    # range(max_retries) is 0 indexed. so range = 0, 1, 2, 3, 4 for max_retries = 5.
    for attempt in range(max_retries):
        if method == "POST":
            response = page.request.post(url, headers=headers, **kwargs)
        elif method == "PUT":
            response = page.request.put(url, headers=headers, **kwargs)
        elif method == "GET":
            response = page.request.get(url, headers=headers, **kwargs)
        elif method == "DELETE":
            response = page.request.delete(url, headers=headers, **kwargs)
        else:
            logging.error("Unexpected method: %s", method)
            raise RuntimeError(f"Unexpected method in request_with_retry: {method}")

            # 429, 503 are the HTTP status codes SharePoint sends when requests fail
        if response.status not in (429, 503):
            logging.debug("URL: %s, \n Status: %s", url, response.status)
            log_rate_limit(response)
            if response is None:
                raise RuntimeError(f"Request to {url} returned None.")
            return response

        retry_after = extract_retry_after(response)
        if retry_after:
            logging.warning("Request are being throttled for %s seconds", retry_after)
            time.sleep(retry_after)
        elif response:
            logging.warning(
                "Throttled with no Retry-After: %s - Retrying in %s seconds",
                response.status,
                2**attempt,
            )
            time.sleep(
                2**attempt
            )  # exponential backoff is fine because max_retries is 0-indexed

    logging.error("Failed to get response from %s", url)
    raise RuntimeError(f"Failed to get response from {url}")


def get_request_digest(page: Page, site_url: str) -> str:
    """
    Returns a digest by querying the site_url.
    SharePoint requires a valid X-RequestDigest header for state-changing operations like
    POST, PUT and DELETE.
    """

    # sends a request to fetch context info from the endpoint
    response = request_with_retry(
        page,
        "POST",
        f"{site_url}/_api/contextinfo",
        # force the response the be in json, otherwise returns XML
        headers={"Accept": "application/json;odata=verbose"},
    )

    if not response.ok:  # response.ok returns a bool
        logging.error("Get digest failed: %s - %s", response.status, response.text())
        raise RuntimeError(f"Get digest failed: {response.status} - {response.text()}")
    data = response.json()  # returns parsed json

    # go through bunch of arrays to get the digest
    digest = data["d"]["GetContextWebInformation"]["FormDigestValue"]
    return digest
