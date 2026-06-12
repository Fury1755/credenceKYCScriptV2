"""This module contains helper functions to parse urls"""

import logging
from urllib.parse import parse_qs, urlparse


def get_url_id(url: str) -> str:
    """
    This function returns relative ids from a raw url.
    Does NOT decode the url.
    """

    # urllib.parse is part of the Python standard library
    # urlparse returns a ParseResult object (named tuple-like object)
    parsed = urlparse(url)

    # returns a dictionary of strings, each key is a parameter name
    qs = parse_qs(parsed.query)

    # just access the dict with .get, returns None if key is missing. Enables custom error handling
    encoded_id = qs.get("id", [None])[0]

    # ah yes our custom error handling
    if encoded_id is None:
        logging.error("No id parameter in %s", url)
        raise RuntimeError(f"No id parameter in {url}")

    return encoded_id


def get_excel_relative_url(url: str) -> str:
    """Gets the relative URL of the Excel file from the "Copy link" provided URL"""

    parsed = urlparse(url)
    if parsed:
        output: str = parsed.path
        if output.startswith("/:x:/r"):
            # trim the start, those prefixes are for sharing links and
            #  should not be in the relative url
            output = output[6:]  # Return everyhing after the first six chars
        return output

    logging.error("Could not extract relative url from %s", url)
    raise RuntimeError("Failed to extract relative url from Excel URL")
