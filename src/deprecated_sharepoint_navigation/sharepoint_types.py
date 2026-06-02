"""
This module contains custom TypedDicts for SharePoint responses because
response.json() returns different types of dicts (mainly folder and files).
"""

# DO NOT NAME MODULES 'types.py' THAT STHE NAME OF A STANDARD LIB MODULE

# A TypedDict is a type hint that lets you specify which types certain values
#  should return. Without this, Dict[str, any] would be used instead which is
#  dangerous?

# It should be noted that actual classes are not created during runtime. They are
#  used for static analysis, not for runtime type checking.

# A TypedDict doesnt have to include all the typings for K-V pairs, just the ones that
#  you plan to use (personally im gonna make great use of ServerRelativeUrl)

from typing import TypedDict, Required, List, Dict


class SharePointFile(TypedDict):  # use PascalCase for classes
    """when SharePoint returns list of files"""

    Name: Required[str]
    ServerRelativeUrl: Required[str]
    Length: Required[int]
    TimeLastModified: Required[str]


class SharePointFolder(TypedDict):
    """when it returns list of folders"""

    Name: Required[str]
    ServerRelativeUrl: Required[str]
    ItemCount: Required[int]
    TimeLastModified: Required[str]
    results: Required[List[Dict]]


# for /$value endpoints, SharePoint returns raw bytes
#  no need to make a class for that
