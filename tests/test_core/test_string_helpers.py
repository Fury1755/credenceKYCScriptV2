"""This module tests the string_helpers module."""

from core.string_helpers import best_match_item, get_next_name
from hypothesis import given, strategies as st, settings
import pytest


@settings(max_examples=999)
@given(st.text(), st.lists(st.text(), min_size=1))
def test_exact_match_is_returned(query: str, extra):
    """
    This test tests whether best_match_item
    consistently returns the best match.
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
