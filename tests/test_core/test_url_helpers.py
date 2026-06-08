'''This module does parameterized tests for url_helpers.py'''

from core.url_helpers import get_url_id
import pytest

@pytest.mark.parametrize("url, expected_id",
                         [("https://sharepoint.com/sites/FINANCE/?id=12345", "12345"),
                          ("Nonsensical url, ?id=12345", "12345"),
                          ("hoasndujniefjjankfwjn&?id=awra&viewid=aifuaifj", "awra")
                          ]
)
def test_get_url_id(url: str, expected_id: str):
    '''This test asserts get_url_id returns anything and everything between ?id=
    and '&'
    '''

    result = get_url_id(url)
    assert result == expected_id

@pytest.mark.parametrize("url",[
    ("https://example_url?id="),
    ("https://pytest")
])
def test_get_url_id_missing(url: str):
    '''This function tests if a url with no id parameter raises the correct error.'''
    with pytest.raises(RuntimeError, match="No id parameter in"):
        # uses re.search internally to find if the error msg contains the
        #  matching substring
        get_url_id(url)
