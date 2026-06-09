"""This module creates 'contents' dictionaries (the type that get_folders_and_files returns)"""

from typing import List, Literal, Any


def set_nested(keys: List[str], value: Any):
    """
    Creates a nested dictionary used to simulate 'contents' dictionaries.

        Args:
            keys(List[str]): A list that represents how many nests you want.

        Returns:
            dict: A dictionary with nested contents in nesting order of 'keys'

    """

    # root is the reference to the entire dict
    root = {}

    # current is a pointer to the innermost dict we work on
    current = root
    for key in keys:
        # .setdefault is a dict method that
        #  creates a new key-{} pair inside the dict it is called on.
        # we are chaining it with the for loop, so it's not magic, just iteration.
        current = current.setdefault(key, {})
    current[keys[-1]] = value

    return root


def create_contents(
    content: Literal["Files", "Folders"], other_nests: List[str] | None, value: Any
):
    """
    Creates empty 'contents' dictionaries (the type that get_folders_and_files returns).
    Used to help with tests to validate existence of keys; the contents are empty except for
    the innermost dict.

        Args:
            content(Literal): Whether the contents contain "Files" or "Folders" (mutually exclusive)
            other_nests: A list of the keys you want nested within the output dict.
                        Input None if file.
            value: If you want the innermost dict to take on a value

        Returns:
            dict: Returns a dictionary with nested "content" corresponding to the specified Literal.
                The dictionary is empty except for the innermost dict.

        Raises:
            ValueError: On argument mismatches between 'content' and 'other_nests'
            (e.g. passed nests to a File object)
    """

    if content == "Files":
        # Precondition: other_nests should be empty if literal is "Files"
        if other_nests is not None:
            raise ValueError("Content 'Files' should not have nested objects inside.")
        # append 'results' to the test: at the moment,
        return set_nested([content, "results"], value)

    if content == "Folders":
        nested_keys = [content, "results"]
        # no nesting for an empty folder
        if other_nests is None:
            return set_nested(nested_keys, value)
        nested_keys.extend(other_nests)
        return set_nested(nested_keys, value)
