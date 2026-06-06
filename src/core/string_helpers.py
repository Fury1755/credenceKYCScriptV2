"""
This module is responsible for all things string related,
such as fuzzy matching.
I/O are purely strings.
"""

import rapidfuzz
from typing import List
import logging


def best_match_item(query: str, choices: List[str], cutoff: int = 80) -> str:
    """Returns a single matching string from a list of strings."""

    # DbC: assert empty strings should not be queries, as they have no meaning
    if query == "":
        logging.error("Query %s passed to best_match_item is an empty string!", query)
        raise ValueError("Empty string passed to best_match_item")

    # DbC: assert that empty strings [] and None should not be passed to 'choices'
    if not choices:
        logging.error("Empty list/None passed to best_match_item! Query: '%s'" \
        ", choices: %s", query, choices)
        raise ValueError("Argument 'choices' passed to best_match_choices is falsy")

    # process.extract returns a List of tuples corresponding to the limit
    matches: List[tuple] = rapidfuzz.process.extract(
        query, choices, limit=1, score_cutoff=cutoff
    )
    if not matches:
        logging.debug(
            "No good match found in best_match_item.\n Query: %s \n Search list: %s",
            query,
            choices,
        )
        raise LookupError("No match found by best_match_item")

    # matches[0] gets the first (and only) matching tuple
    # matches[0][2] gets the index of the match in the choices list
    # choices[matches[0][2]] returnst the indexed element in the list
    return choices[matches[0][2]]


def get_next_name(last_company_name: str, name_list: List[str]) -> str:
    """Returns the next company, alphabetically sorted, in name_list after last_company_name."""

    # DbC: name_list and last_company_name should not be falsy (empty or None)
    if not name_list and last_company_name:
        logging.error("Falsy arguments passed to get_next_name: last_company_name == " \
        "'%s', name_list == %s", last_company_name, name_list)
        raise ValueError("Invalid arguments passed to get_next_name")

    # handles empty entries in name_list. Again, revealed through testing.

    if "" in name_list:
        raise ValueError("Empty string present in name_list!")

    # duplicate name handling. unlikely to ever occur, but this weakness was revealed
    #  through property testing.

    # dict.fromkeys() preserves order, unlike set()
    unique_names = list(dict.fromkeys(name_list))

    new_list = sorted(unique_names, key=str.lower)
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
