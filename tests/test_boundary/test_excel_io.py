'''This module conducts unit tests for excel_io.py'''

from boundary.excel_io import download_excel
from factories.mock_response import MockAPIResponse
from unittest.mock import patch, MagicMock


@patch('boundary.excel_io.openpyxl.load_workbook')
@patch('boundary.excel_io.request_with_retry') # patch the local function
# passes a MagicMock object into the parameter
# the order it is passed into the function is from bottom-most
#  decorator to top
# openpyxl.load_workbook is an independent external dependency
#  within the function. It's return value does NOT follow from mocking
#  a request, therefore it must be mocked as well.
def test_download_excel(mock_request, mock_workbook):
    '''This function tests if download_excel can handle various responses.'''

    mock_endpoint = "https://doesntmatter.com"
    mock_response = MockAPIResponse(mock_endpoint, body = b"test_bytes")
    mock_request.return_value = mock_response

    # we are focusing on the response, so we don't need
    #  an actual value for the excel wb.
    fake_wb = MagicMock()
    mock_workbook.return_value = fake_wb
    wb = download_excel(MagicMock(), MagicMock(), mock_endpoint)

    # assert that
    # 1. the function ran successfully
    # 2. it returned the exact object we returned by load_workbook
    #     (MagicMock())
    # 'is' asserts equality by reference (memory addresses)
    # '==' checks value equality
    # although '==' works here, use 'is'
    assert wb is fake_wb
