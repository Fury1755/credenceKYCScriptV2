"""
This module conducts unit tests for excel_io.py.
"""

from boundary.excel_io import download_excel, upload_excel
from factories.mock_response import MockAPIResponse
from unittest.mock import patch, MagicMock
import pytest


@pytest.mark.parametrize("status, ok", [("400", False), ("200", True), ("304", False)])
def test_download_excel(status: int, ok: bool):
    """
    This function tests if download_excel can handle various responses.
    This test is meaningful because it verifies:
    - when ok is true, the correct workbook is returned
    - when ok is false, RuntimeError is raised
    - when ok is false, error message returns response status and response text
    """

    # initialize our response according to the arguments passed
    mock_response = MockAPIResponse(status=status, ok=ok)

    # patch the local function
    with patch("boundary.excel_io.request_with_retry") as mock_request:
        mock_request.return_value = mock_response

        # openpyxl.load_workbook is an independent external dependency
        #  within the function. It's return value does NOT follow from mocking
        #  a request, therefore it must be mocked as well.
        with patch("boundary.excel_io.openpyxl.load_workbook") as mock_workbook:
            fake_wb = MagicMock()
            mock_workbook.return_value = fake_wb
            if not ok:
                # assert that runtimeerror will be raised
                with pytest.raises(RuntimeError) as exc_info:
                    wb = download_excel(
                        MagicMock(), MagicMock(), "raw_url doesnt matter"
                    )
                    assert exc_info.value == (
                        f"Download failed: {mock_response.status} - "
                        f"{mock_response.text()}"
                    )
                    return
            elif ok:
                wb = download_excel(MagicMock(), MagicMock(), "raw_url doesnt matter")
                # assert that
                # 1. the function ran successfully
                # 2. it returned the exact object we returned by load_workbook
                #     (MagicMock())
                # 'is' asserts equality by reference (memory addresses)
                # '==' checks value equality
                # although '==' works here, use 'is'
                assert wb is fake_wb

                return


@pytest.mark.parametrize(
    "text, status, ok", [("feeling good", 200, True), ("tummy ache", 404, False)]
)
def test_upload_excel(text: str, status: int, ok: bool):
    """
    This function tests if upload_excel responds appropriately to various responses.
    This test verifies
    - the correct digest is used in the request
    - the correct bytes are uploaded in the request
    - RuntimeError is correctly thrown when request not ok
    - RuntimeError shows the correct text
    """

    # These earlier functions help to build the request which fetches the response.
    # since we are mocking requests, to ensure coverage, we should mock (and subsequently
    #  test, but in a separate module) these earlier functions.
    with (
        patch("boundary.excel_io.get_request_digest") as mock_digest,
        patch("boundary.excel_io.workbook_to_bytes") as mock_bytes,
        patch("boundary.excel_io.request_with_retry") as mock_request,
    ):
        fake_digest = "hhh"
        mock_digest.return_value = fake_digest
        # by assigning the mock_digest a value instead of a MagicMock,
        #  you test *how* the digest value passes through the test function,
        #  not the get_request_digest function itself.

        fake_bytes = b"blah blah blah"
        mock_bytes.return_value = fake_bytes
        mock_response = MockAPIResponse(text=text, ok=ok, status=status)
        mock_request.return_value = mock_response
        # We can pass practically all args as a MagicMock because
        #  we intercept and mock everything we want to test and trace.
        if not ok:
            with pytest.raises(RuntimeError) as exc_info:
                upload_excel(
                    MagicMock(),
                    MagicMock(),
                    MagicMock(),
                    "this has to be a str otherwise urllib fails",
                )

            # with pytest.raises exits the block as soon as the error is raised.
            print(exc_info.value)
            print(f"Upload failed: {mock_response.status} - {mock_response.text()}")
            assert (
                str(exc_info.value)
                == f"Upload failed: {mock_response.status} - {mock_response.text()}"
            )

            return

        # don't forget: you have to call the function to initialize the mocked functions!
        upload_excel(
            MagicMock(), MagicMock(), MagicMock(), "again, this cant be MagicMock"
        )
        # intercept and see if our arguments were passed to mock_response
        kwargs = mock_request.call_args.kwargs
        assert kwargs["headers"]["X-RequestDigest"] == fake_digest
        assert kwargs["data"] == fake_bytes
