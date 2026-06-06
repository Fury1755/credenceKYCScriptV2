"""This module tests the string_helpers module."""

from core.string_helpers import best_match_item, get_next_name
from hypothesis import given, strategies as st, settings
from typing import List
import pytest


@settings(max_examples=999)
# @settings sets the number of test cases
@given(st.text(), st.lists(st.text(), min_size=1))
# @given is a decorator that generates random inputs
# it passes arguments to the function below in the order
#  the arguments in @given are written
def test_exact_match_is_returned(query: str, extra: List[str]):
    """
    This test tests whether best_match_item
    consistently returns the item it's expected to match.
    """
    # we set min_size = 1 because matching empty strings is not meaningful.

    items = [query]
    items.extend(extra)
    try:
        result = best_match_item(query, items, cutoff=80)
    except (ValueError, LookupError):
        # the errors the function is designed to throw
        if items is not None and query != "":
            pytest.fail("best_match_item raised an error even though query is in items")
        else:
            return
    assert result == query

@settings(max_examples=999)
@given(st.text(), st.lists(st.text()))
def test_next_name_is_returned(last_name: str, extra: List[str]):
    '''
    Tests if the function get_next_name returns the next lexicographical
    name in a list.
    '''

    # this guarantees extra will never be empty
    extra.append(last_name)
    # we deduplicate the test cases, otherwise
    #  next_name_index will be returned incorrectly
    extra = list(dict.fromkeys(extra))

    sorted_list = sorted(extra, key=str.lower)

    # to keep type checker happy.
    # unless last_name becomes the last element, next_name_index
    #  will always be initialized to the correct value. if last_name
    #  is the last element, ValueError will be thrown and the value of next_name_index
    #  won't matter.
    next_name_index = 1

    # check if last_name is not the last element in the list,
    #  so that we don't go out of bounds when getting next_name_index
    if last_name != sorted_list[-1]: # len is not zero indexed!
        next_name_index = sorted_list.index(last_name) + 1

    def is_fail(last_name: str, sorted_list: List[str]) -> bool:
        '''Runs when the test function throws ValueError.
        Returns False if the test fails
        (e.g. errors are thrown when it shouldn't be thrown)'''

        # i feel this is more robust than throwing everything in the except block

        # if last_name is the last element, ValueError is allowed. return True.
        if last_name == sorted_list[-1]: # -1 is the index of last item
            return True

        # if last_name and sorted_list are invalid inputs, ValueError is allowed.
        if not last_name and sorted_list:
            return True

        # if empty string in name_list, allow it.
        if "" in sorted_list:
            return True

        # on everything else (failure cases not defined), return False
        return False

    try:
        next_name = get_next_name(last_name, extra)
    except ValueError:
        if is_fail(last_name, sorted_list) is False:
            pytest.fail("ValueError occured even though both inputs were valid")
        else:
            return

    assert next_name == sorted_list[next_name_index]
