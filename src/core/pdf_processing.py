"""This module processes PDFs."""

import pdfplumber
import re
import io
from pdfplumber.page import Page
from core.individual import Individual
from typing import List


def process_pdf(response_pdf: io.BytesIO) -> List[Individual]:
    """Reads the pdf file and returns a list of Individuals"""
    with pdfplumber.open(response_pdf) as pdf:

        def contains_text_row(table, target: str):
            # returns row number
            not_found = -1
            for r, row in enumerate(table):
                for cell in row:
                    if cell:
                        if re.search(rf".*{target}.*", cell):
                            return r
            return not_found

        def delete_text_row(table, row_number: int, before_after: str):
            if before_after != "PRECEDING" and before_after != "SUCCEEDING":
                print("Incorrect input parameter in delete_text_row")
                return table
            if before_after == "PRECEDING":
                del table[
                    : row_number + 1
                ]  # IMPORTANT :row_number does not include itself
            if before_after == "SUCCEEDING":
                del table[row_number:]  # IMPORTANT row_number: includes itself
            deleted_table = table  # this is necessary knowledge for tables in python
            return deleted_table

        def shareholder_page(pg: Page):
            page = pg
            words = page.extract_words()
            shareholder_x0 = -1
            identification_x0 = -1
            identification_x1 = -1
            shareholder_found = False
            for word in words:
                if re.search(r"Shareholder.*", word["text"]):
                    # rewrite settings
                    shareholder_x0 = word["x0"] - 0.1
                    shareholder_found = True

                # shareholder_found just means Identification is happening after shareholder
                if re.search(r"Identification", word["text"]) and shareholder_found:
                    identification_x0 = word["x0"] - 0.1
                    identification_x1 = word["x1"] + 0.1

            # now we change settings
            shareholder_settings = {
                "vertical_strategy": "explicit",
                "explicit_vertical_lines": [
                    shareholder_x0,
                    identification_x0,
                    identification_x1,
                ],
                "horizontal_strategy": "lines",
            }

            table = page.extract_table(shareholder_settings)
            if table:
                shareholder_row = contains_text_row(table, r"Shareholder\(s\)")
                delete_text_row(table, shareholder_row, "PRECEDING")
                address_row = contains_text_row(table, "Address")
                delete_text_row(table, address_row, "PRECEDING")
                includes_row = contains_text_row(table, "Includes")
                delete_text_row(table, includes_row, "SUCCEEDING")

                for r, row in enumerate(table):
                    for c, cell in enumerate(row):
                        if cell:
                            if re.search(r".*\n.*", cell):
                                # in case the shareholder name is multi line,
                                # implement separate processing for the shareholder cell
                                if re.search(
                                    r"238A THOMSON ROAD.*", cell, flags=re.DOTALL
                                ):
                                    # replace \n with a single space so re.sub works properly
                                    cell = re.sub(r"\n", " ", cell)
                                    cell = re.sub(
                                        r"238A THOMSON ROAD.*",
                                        "",
                                        cell,
                                        flags=re.DOTALL,
                                    )
                                    cell = re.sub(r"\n", " ", cell)  # replace again
                                    table[r][c] = cell.strip()
                                else:
                                    table[r][c] = re.sub(r"\n.*", "", cell)

            return table

        def officer_page(pg: Page):
            page = pg
            words = page.extract_words()

            officer_found = False
            officer_x0 = -1
            identification_x0 = -1
            identification_x1 = -1
            for word in words:
                if re.search(r"Officer", word["text"]):
                    officer_found = True
                    officer_x0 = word["x0"] - 0.1
                if re.search(r"Identification", word["text"]) and officer_found:
                    if identification_x0 == -1:
                        identification_x0 = word["x0"] - 0.1
                        identification_x1 = word["x1"] + 0.1

            officer_settings = {
                "vertical_strategy": "explicit",
                "explicit_vertical_lines": [
                    officer_x0,
                    identification_x0,
                    identification_x1,
                ],
                "horizontal_strategy": "lines",
            }

            table = page.extract_table(officer_settings)
            if table:
                for r, row in enumerate(table):
                    for c, cell in enumerate(row):
                        if cell:
                            if re.search(r".*\n.*", cell):
                                row[c] = re.sub(r"\n.*", "", cell)

                for r in range(len(table) - 1, -1, -1):
                    for cell in table[r]:
                        if cell:
                            if re.search(r".*\d to \d", cell):
                                del table[r]
                            if re.search(r".*Name.*", cell):
                                del table[r]

            if table:
                shareholder_row = contains_text_row(table, "Shareholder")
                delete_text_row(table, shareholder_row, "SUCCEEDING")
                officer_row = contains_text_row(table, "Officer")
                delete_text_row(table, officer_row, "PRECEDING")

            return table

            # DEBUG
            # img = page.to_image(resolution = 150)
            # img.debug_tablefinder(officer_settings)
            # img.save(r"C:\Users\Intern\Downloads\split_statements\debug.png")

        def flatten_lists(imput, result: list):
            for item in imput:
                if isinstance(item, list):  # type checking
                    if len(item) == 2:
                        for itemitem in item:
                            if isinstance(itemitem, str):
                                result.append(item)
                                break

                            else:
                                flatten_lists(item, result)
                    else:
                        flatten_lists(item, result)

            return result

        def remove_duplicates(result: list):
            seen = set()
            for pair in result:
                key = tuple(pair)
                if key not in seen:
                    seen.add(key)
            return list(seen)

        def remove_names(result: list, name: str):
            return [
                item
                for item in result
                if not any(name in itemitem for itemitem in item)
            ]

        def remove_empty_tuples(result: list):
            return [
                item for item in result if not all(itemitem == "" for itemitem in item)
            ]

        def process_list(result: list):
            result = remove_duplicates(flatten_lists(result, []))
            result = remove_empty_tuples(result)
            result = remove_names(result, "TATT CHONG")
            result = remove_names(result, "SIOK LENG")
            return result

        # get shareholders and officers
        shareholder_table = []
        officer_table = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if "Shareholder" in text:
                # note that shareholders can be split across different pages.
                temp_list = shareholder_page(page)
                if temp_list not in shareholder_table:
                    shareholder_table.append(temp_list)

            if "Officer(s)" in text:
                temp_list = officer_page(pdf.pages[i])
                if temp_list not in officer_table:
                    officer_table.append(temp_list)

        shareholder_table = process_list(shareholder_table)
        officer_table = process_list(officer_table)
        # now we have two lists of shareholders

        print("shareholders: ", shareholder_table)
        print("officers: ", officer_table)

        # now we return the KAH class
        shareholder_list = []
        for shareholder_tuple in shareholder_table:
            temp_kah = Individual(
                f"{shareholder_tuple[0]}",
                "-",
                shareholder_tuple[1],
                "-",
                "-",
                True,
                False,
                False,
                None,
            )
            shareholder_list.append(temp_kah)

        officer_list = []
        for officer_tuple in officer_table:
            temp_kah = Individual(
                officer_tuple[0],
                "-",
                officer_tuple[1],
                "-",
                "-",
                True,
                False,
                False,
                None,
            )
            officer_list.append(temp_kah)
        kah_dict = {"officers": officer_list, "shareholders": shareholder_list}
        officers = kah_dict.get("officers", [])
        shareholders = kah_dict.get("shareholders", [])
        output: List[Individual] = []
        officer_by_name = None
        if officers:
            officer_by_name = [officer.name for officer in officers]
            for officer in officers:
                officer.role = "DIRECTOR"
                output.append(officer)

        if shareholders:
            for shareholder in shareholders:
                if officer_by_name is not None:
                    if shareholder.name in officer_by_name:
                        shareholder.role = "SHAREHOLDER/DIRECTOR"
                        continue
                    else:
                        shareholder.role = (
                            "SHAREHOLDER"  # messy logic. rewrite when free
                        )
                else:
                    shareholder.role = "SHAREHOLDER"

                output.append(shareholder)

        # deduplicate output again because my logic is not perfect
        unique_output = []
        seen = {}
        for individual in output:
            key = (individual.name, individual.role)
            if key not in seen:
                seen[key] = True
                unique_output.append(individual)
        return unique_output
