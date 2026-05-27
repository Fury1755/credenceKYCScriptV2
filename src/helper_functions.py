'''
helper functions
includes:
- get_url_id
- check_rate_limit
'''

from urllib.parse import urlparse, parse_qs
from playwright.sync_api import APIResponse
import logging

def get_url_id(url: str) -> str:
    '''
    This function gets ids from a raw url
    Does NOT decode the url
    '''

    # urllib.parse is part of the Python standard library
    # urlparse returns a ParseResult object (named tuple-like object)
    parsed = urlparse(url)

    # returns a dictionary of strings, each key is a parameter name
    qs = parse_qs(parsed.query)


    # just access the dict with .get, returns None if key is missing. Enables custom error handling
    encoded_id = qs.get('id', [None])[0]

    #ah yes our custom error handling
    if encoded_id is None:
        error_msg = "No id parameter in %s", url
        logging.error(error_msg)
        raise RuntimeError(error_msg)

    return encoded_id

def log_rate_limit(response: APIResponse):
    '''
    takes a page's response as an argument and checks for rate limit
    '''

    headers: dict[str, str] = response.headers
    rate_limit_dict: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower().startswith("ratelimit"):
            rate_limit_dict[key] = value

    if rate_limit_dict: # yes, you can check for empty dicts this way
        logging.warning("Rate limit detected: ")
        for key, value in rate_limit_dict.items():
            logging.warning("%s - %s", key, value)
