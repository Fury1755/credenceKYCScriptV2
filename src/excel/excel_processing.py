'''
This module handles the logic and processing of workbooks.
The input and output should be workbooks.
'''

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from typing import Union, Optional
import logging

def get_latest_company_name(wb: Workbook, current_letter: str) -> str:
    '''
    This module reads the latest company that has been KYC-ed
    from the spreadsheet corresponding to current_letter.
    Note that worksheets are mutable inside a Workbook.
    '''

    if len(wb.worksheets) > 0: #initialize and check
        ws = wb.worksheets[0]
    else:
        raise ValueError("No worksheets found in searched workbook")

    ws_found = False

    for sheet in wb.worksheets: #get sheet corresponding to current_letter
        if sheet.title.strip() == current_letter:
            ws = sheet
            ws_found = True

    if not ws_found:
        raise ValueError(f"No sheet named {current_letter} found")

    last_cell = get_last_filled_cell(ws, "B")

    if last_cell:
        logging.info("%s", last_cell.value)
        print(last_cell.value)
        return str(last_cell.value)

    logging.error("No cell found in worksheet %s", ws.title)
    raise ValueError(f"No cell found in worksheet '{ws.title}'")

def get_last_filled_cell(ws: Worksheet, column: Union[int,str]) -> Optional[Cell]:
    '''
    Returns the last non-None cell in the given column.
    Union has the same effect as the pipe operator | but is compatible with Python < 3.10
    In fact, Optional[X] just means Union[X, None]
    '''

    # Convert letter to number
    if isinstance(column, str):
        from openpyxl.utils import column_index_from_string
        col_idx = column_index_from_string(column)
    else:
        col_idx = column

    for row in range(ws.max_row, 0, -1):  # parameters are range(start, stop, step)
        cell = ws.cell(row=row, column=col_idx)
        if cell.value is not None:
            return cell
    return None
