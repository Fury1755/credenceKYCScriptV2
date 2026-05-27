'''
This module handles the logic and processing of workbooks.
The input and output should be workbooks.
'''
import openpyxl
from openpyxl import Workbook

def read_latest_company(wb: Workbook, CURRENT_LETTER: str) -> Workbook:
    '''
    This module reads the latest company that has been KYC-ed
    from the spreadsheet corresponding to CURRENT_LETTER.
    Note that worksheets are mutable inside a Workbook.
    '''

    if len(wb.worksheets) > 0: #initialize and check
        ws = wb.worksheets[0]
    else:
        raise ValueError("No worksheets found in searched workbook")

    ws_found = False

    for sheet in wb.worksheets: #get sheet corresponding to CURRENT_LETTER
        if sheet.title.strip() == CURRENT_LETTER:
            ws = sheet
            ws_found = True

    if not ws_found:
        raise ValueError(f"No sheet named {CURRENT_LETTER} found")

    ws["E7"] = "kiki do you love me"  # worksheets are mutable
    print("Workbook modified.")
    return wb
