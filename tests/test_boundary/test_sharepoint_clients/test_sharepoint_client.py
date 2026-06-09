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

    Does not test error handling.

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

        # simulates the json structure of what sharepoint returns
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


def test_create_folder():
    """
    This test verifies that:
    - correct arguments are passed to get_request_digest
    - correct upload endpoint is constructed
    - response is correctly unwrapped (implicit in the example json)
    - request arguments are correctly passed

    Does not test error handling.
    """

    with (
        patch("boundary.response_helpers.get_request_digest") as mock_request_digest,
        patch.object(SharePointClient, "_walk_folder") as mock_walk_folder,
        patch.object(SharePointClient, "request") as mock_request,
        patch.object(SharePointClient, "_build_client_query") as mock_build_query,
    ):
        mock_digest = "fake digest"
        names = [
            "SIR GET DOWN",
            "SIR GET DOWN NOW",
            "Ayyy, ayyy",
            "ayyy",
            "to the windowww",
        ]
        mock_response_json = {
            "Files": {
                "results": [
                    {"Name": names[0]},
                    {"Name": names[1]},
                    {"Name": names[2]},
                ]
            },
            "Folders": {
                "results": [{"Name": names[3]}, {"Name": names[4]}],
            },
        }
        mock_request_digest.return_value = mock_digest
        mock_walk_folder.return_value = MockAPIResponse(
            "doesnt matter", mock_response_json
        )

        mock_site_url = "fake_site_url"
        mock_relative_url = "fake_relative_url"
        # keep the urls as actual strings; we need them to verify the endpoint.
        mock_page = MagicMock()
        dummy = SharePointClient(
            mock_page,
            mock_site_url,
            mock_relative_url,
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        mock_folder_name = "fake_folder_name"
        fake_endpoint = (
            f"{mock_site_url}/_api/web/GetFolderByServerRelativeUrl"
            f"('{mock_relative_url}')"
            f"/Folders/add('{mock_folder_name}')"
        )

        dummy.create_folder(mock_folder_name)

        request_positional_args = (
            "POST",
            fake_endpoint,
        )
        header_value = {
            "Accept": "application/json;odata=verbose",
            "X-RequestDigest": mock_digest,
        }

        mock_request_digest.assert_called_once_with(mock_page, mock_site_url)
        mock_request.assert_called_once_with(
            *request_positional_args, headers=header_value
        )
        mock_build_query.assert_called_once_with(mock_folder_name)
