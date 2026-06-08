"""
This module contains unit tests for pdf_io.py
"""

from boundary.pdf_io import download_pdf
from unittest.mock import patch, MagicMock
from factories.mock_response import MockAPIResponse
from boundary.sharepoint_exceptions import SharePointResponseError
import pytest


@pytest.mark.parametrize(
    "server_relative_url, ok",
    [("blah blah", True), ("no", False)],
)
def test_download_pdf(server_relative_url: str, ok: bool):
    """
    This test verifies that:
    - arguments are correctly used to construct correct endpoints
    """

    with patch("boundary.pdf_io.request_with_retry") as mock_request:
        mock_response = MockAPIResponse(ok=ok)
        mock_request.return_value = mock_response
        fake_page = MagicMock()
        fake_site_url = "blah"
        fake_file_item = {"ServerRelativeUrl": server_relative_url}
        if ok:
            download_pdf(fake_page, fake_site_url, fake_file_item)
            (page, method, endpoint) = mock_request.call_args.args

            # assert the args were passed correctly
            assert page is fake_page
            assert method == "GET"
            assert endpoint == (
                f"{fake_site_url}/_api/web/GetFileByServerRelativeUrl"
                f"('{fake_file_item['ServerRelativeUrl']}')/$value"
            )

        else:
            with pytest.raises(SharePointResponseError) as exec_info:
                download_pdf(fake_page, fake_site_url, fake_file_item)
            assert (
                str(exec_info.value)
                == f"PDF download failed - response: {mock_response.status}"
            )
            return
