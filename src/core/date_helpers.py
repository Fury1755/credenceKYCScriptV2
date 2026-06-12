"""
This module holds date functions that parse and compare dates.
"""

import logging
import re
from typing import List


def parse_date_from_name(name_input: str) -> str | None:
    """
    This function takes a string containing a possible date
     and returns a string in the same formate as TimeLastModified
    so they can be lexicographically compared.

    Args:
        name(str): 28 May 2024

    Returns:
        A string in a DateTime format (e.g. '2024-05-24T10:00:00Z'),
        or None if nothing found.

    Defaults to:
            'f{year}-12-30T00:00:Z' if the month is missing.
            Currently does not return the day if the day is inside.

    Note:
        The time (everything that comes after 'T') is fixed at 00:00:00,
        because it is unlikely the name will contain information about the hour it
        was posted at. We fix the date to be the highest, because human-typed dates are reliable.
        (thanks audrey)

        If FY is in the name, we increase the year by one, otherwise it wouldn't be named 'FY' if
        the year wasn't already over.
    """

    # remove trailing whitespaces
    name = name_input.strip()

    # precondition: name cannot be None
    if name is None:
        raise ValueError("Empty string passed to parse_date_from_name")

    year = None
    # first extract the year. We do this by matching cases
    # let's first start by matching the most definite case:
    #  20\d{2} surrounded by spaces on both sides is definitely a year.
    match = re.search(r"\b20\d{2}\b", name)
    if match:
        year = match[0]

    # next in priority is the case where it is the last in the name.
    match = re.search(r"\b20\d{2}", name)
    if match:
        year = match[0]

    # finally the most unlikely: the file/folder name starts with the year
    #   we still consider this though
    match = re.search(r"20\d{2}\b", name)
    if match:
        year = match[0]
        logging.warning("File/folder name '%s' is strange", name_input)

    if year is None:
        return None

    # DbC: assert year is four digits
    if not (len(year) == 4 and year.isdigit()):
        logging.error(
            "Error: year '%s' found in parse_date_from name is not four digits!", year
        )
        raise ValueError("Logic error in pure function parse_date_from_name")

    # increase year by 1 if FY in name
    if "FY" in name_input:
        year = int(year) + 1

    # now we search for relevant months
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    truncated_months = [month[:3] for month in months]
    all_months = months + truncated_months
    month_index = None

    for i, each_month_index in enumerate(all_months):
        if each_month_index in name:
            month_index = i
            break

    if month_index is None:
        logging.info("Parse date success: '%s-12-30T00:00:00Z'", year)
        return f"{year}-12-30T00:00:00Z"

    month = month_index % 12 + 1

    logging.info("Parse date success: '%s-%02d-30T00:00:00Z'", year, month)
    return f"{year}-{month:02d}-30T00:00:00Z"


def validate_dict(item: dict, required_keys: List[str]) -> None:
    """Raises KeyError with the first missing path
    Raises TypeError if all the keys are not str"""
    for key in required_keys:
        keys = key.split(".")
        current = item
        for key in keys:
            if not isinstance(current, dict):
                raise TypeError(
                    f"Expected type dict at path {key} but got {type(current)}"
                )
            if key not in current:
                raise KeyError(f"Required path {key} not in {item}")
            current = current[key]  # type: ignore


def get_effective_date(file_or_folder: dict) -> str:
    """
    Takes a SharePoint dictionary as input (files: {}, folders: {})
    """

    # precondition: has keys Name, TimeLastModified
    validate_dict(file_or_folder, ["Name", "TimeLastModified"])

    # the file name takes precedence
    name_date = parse_date_from_name(file_or_folder["Name"])
    if name_date:
        return name_date

    # prioritize this over TimeLastModified
    list_item = file_or_folder.get("ListItemAllFields")
    if isinstance(list_item, dict):
        modified = list_item.get("Modified")
        if modified:
            return modified

    return file_or_folder["TimeLastModified"]
