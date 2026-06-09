"""
This module tests pure methods in the SharePointClientParser class.
"""

from typing import List
from boundary.sharepoint_clients.sharepoint_client import SharePointClientParser
import pytest


@pytest.mark.parametrize(
    "contents, expected_names, ok",
    [
        (
            {"Folders": [{"Name": "awdawfd"}, {"Name": "vofe"}]},
            ["awdawfd", "vofe"],
            True,
        ),
        ({"Not ok": [{"something": "irrelevant"}]}, ["doesnt matter"], False),
    ],
)
def test_get_folder_names_from_contents(
    contents: dict[str, list],
    expected_names: List[str],
    ok: bool,
):
    """
    Tests if get_next_company properly returns the appropriate folder names
    from a dictionary of contents.

    This test validates:
    - correct output by the function
    - correct custom error handling (ValueError, KeyError) by the function
    """
    # again, our focus is not on whether the called functions work;
    #  but rather how they are called, and how their results
    #  are used.

    dummy = SharePointClientParser()

    if not ok:
        with pytest.raises((KeyError, ValueError)):
            dummy.get_folder_names_from_contents(contents)
        return

    folder_names = dummy.get_folder_names_from_contents(contents)
    for name in expected_names:
        assert name in folder_names
