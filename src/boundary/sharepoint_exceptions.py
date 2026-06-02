"""This module contains custom SharePoint errors."""
# Custom errors provide more information at a glance
#  than a generic RuntimeError.
# These classes exist to solely provide semantic meaning
#  at the appropriate time.


class SharePointError(Exception):
    """The base exception for SharePoint errors."""


class SharePointContractViolation(SharePointError):
    """DbC contract violation in a SharePoint object."""


class SharePointResponseError(SharePointError):
    """API response error (likely malformed request endpoint)"""


class SharePointDuplicateError(SharePointError):
    """
    Duplicate items found through string matching when only one
    was expected
    """


class SharePointKeyError(SharePointError):
    """
    Key not found in a dictionary from SharePoint response
    """
