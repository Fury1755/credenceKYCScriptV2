"""
This module tests methods in SharePointClient.
SharePointClient is an orchestration class that contains other classes as components
to interact and process SharePoint site navigation.
"""

from boundary.sharepoint_clients.sharepoint_client import SharePointClient
from factories.mock_response import MockAPIResponse
from unittest.mock import patch, MagicMock


def test_get_next_company_coarse():
    """
    Coarsely tests the function get_next_company.
    The purpose is to document the function's external behaviour,
    which should be consistent post-refactor.

    The test verifies that:
    - get_next_company, when called with a mock object 'response_json',
      correctly passes the next company's name to its instantiated output.

    """

    with (
        patch.object(SharePointClient, "_walk_folder") as mock_walk_folder,
        patch("core.string_helpers.best_match_item") as mock_best_match_item,
        patch.object(SharePointClient, "_decide_folder") as mock_decide_folder,
        patch.object(SharePointClient, "_get_item_data") as mock_get_item_data,
        patch.object(SharePointClient, "_build_client_query") as mock_build_query,
    ):
        folder_names = ["Apparation Pte Ltd", "Aquatic Horsea Venture Capital"]
        mock_best_match_item.return_value = folder_names
        mock_get_item_data.return_value = folder_names
        mock_decide_folder.return_value = "mock ServerRelativeUrl"
        mock_response_json = {
            "d": {
                "Files": {"results": [{"Name": "file1"}, {"Name": "file2"}]},
                "Folders": {
                    "results": [{"Name": folder_names[0]}, {"Name": folder_names[1]}]
                },
            }
        }

        mock_walk_folder.return_value = MockAPIResponse(
            "doesnt matter", mock_response_json, 200
        )

        dummy = SharePointClient(
            MagicMock(),
            "dummy site url",
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        dummy.get_next_company(folder_names[0])

        assert mock_build_query.call_args.args[0] == folder_names[1]
