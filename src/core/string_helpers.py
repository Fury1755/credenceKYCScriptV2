"""
This module is responsible for all things string related,
such as fuzzy matching.
I/O are purely strings.
"""

import rapidfuzz
from typing import List
import logging


def best_match_item(query: str, items: List[str], cutoff: int = 80) -> str:
    """Returns a single matching string from a list of strings."""

    if query == "":
        logging.error("Query %s passed to best_match_item is an empty string!", query)
        raise ValueError("Empty string passed to best_match_item")

    if not items:
        logging.error("Argument 'items' passed to best_match_items is None")
        raise ValueError("Argument 'items' passed to best_match_items is None")

    # process.extract returns a List of tuples corresponding to the limit
    matches: List[tuple] = rapidfuzz.process.extract(
        query, items, limit=1, score_cutoff=cutoff
    )
    if not matches:
        logging.debug(
            "No good match found in best_match_item.\n Query: %s \n Search list: %s",
            query,
            items,
        )
        raise LookupError("No match found by best_match_item")
    return items[matches[0][2]]


def get_next_name(last_company_name: str, name_list: List[str]) -> str:
    """Returns the next company, alphabetically sorted, in name_list after last_company_name."""
    new_list = sorted(name_list, key=str.lower)
    if last_company_name not in name_list:
        logging.error(
            "Could not find company name '%s' in the list %s",
            last_company_name,
            name_list,
        )
        raise ValueError("Could not find company name in name list.")

    for i, name in enumerate(new_list):
        if name == last_company_name:
            if i < len(new_list) - 1:  # Because len is not zero-indexed
                logging.info("%s", new_list[i + 1])
                return new_list[i + 1]

    logging.error(
        "Could not find any companies beyond %s in %s", last_company_name, name_list
    )
    raise ValueError(f"No companies beyond '{last_company_name}'")
