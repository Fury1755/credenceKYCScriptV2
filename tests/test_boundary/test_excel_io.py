'''
This module conducts unit tests for excel_io.py.
'''

from boundary.excel_io import download_excel
from factories.mock_response import MockAPIResponse
from unittest.mock import patch, MagicMock
import pytest

@pytest.mark.parametrize("status, ok", [
    ("400", False),
    ("200", True),
    ("304", False)
])
def test_download_excel(status: int, ok: bool):
    '''
    This function tests if download_excel can handle various responses.
    This test is meaningful because it verifies:
    - when ok is true, the correct workbook is returned
    - when ok is false, RuntimeError is raised
    - when ok is false, error message returns response status and response text
    '''

    # initialize our response according to the arguments passed
    mock_response = MockAPIResponse(status=status, ok=ok)

    # patch the local function
    with patch('boundary.excel_io.request_with_retry') as mock_request:
        mock_request.return_value = mock_response

        # openpyxl.load_workbook is an independent external dependency
        #  within the function. It's return value does NOT follow from mocking
        #  a request, therefore it must be mocked as well.
        with patch('boundary.excel_io.openpyxl.load_workbook') as mock_workbook:
            fake_wb = MagicMock()
            mock_workbook.return_value = fake_wb
            if not ok:
                # assert that runtimeerror will be raised
                with pytest.raises(RuntimeError) as exc_info:
                    wb = download_excel(MagicMock(), MagicMock(), "raw_url doesnt matter")
                    assert exc_info.value == (f"Download failed: {mock_response.status} - "
                    f"{mock_response.text()}")
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
