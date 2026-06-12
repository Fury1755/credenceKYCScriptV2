"""
This module tests the create_folder function in walk_folder_contents.
Personally, it clarifies the behaviour of create_folder for me, and is inexpensive
to write.
"""

from .walk_folder_contents import create_folder


def test_create_folder():
    """
    A quick, behavioural based test of create_folder.
    """
    properties_list = (str("united investments"), str("random url"), str("random time"))
    result = create_folder([properties_list])

    assert "Folders" in result
    assert "results" in result["Folders"]

    first = result["Folders"]["results"][0]
    print(result)
    print(first)
    assert "united investments" in first["Name"]
    assert "random url" in first["ServerRelativeUrl"]
    assert "random time" in first["TimeLastModified"]
