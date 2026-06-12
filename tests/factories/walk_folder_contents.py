"""
This module creates 'contents' dictionaries (specifically, the dicts that walk_folder returns).
"""

from typing import Any, List, Literal


def set_nested(keys: List[str], value: Any):
    """
    Creates a nested dictionary used to simulate 'contents' dictionaries.

        Args:
            keys (List[str]): A list that represents how many nests you want.
                                Each key nests one layer deeper.
            value (Any): The value you want the innermost nested key to hold.

        Returns:
            dict: A dictionary with nested contents in nesting order of 'keys'

        Note:
            This is a generic abstraction, meant to be usede as a helper function.

    """

    # root is the reference to the entire dict
    root = {}

    # current is a pointer to the innermost dict we work on
    current = root
    for idx, key in enumerate(keys):
        # .setdefault is a dict method that
        #  creates a new key-{} pair inside the dict it is called on.
        # we are chaining it with the for loop, so it's not magic, just iteration.
        if idx < len(keys) - 1:
            current = current.setdefault(key, {})
        else:
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
            value: The value you want the innermost dict to take on.

        Returns:
            dict: Returns a dictionary with nested "content" corresponding to the specified Literal.
                The dictionary is empty except for the innermost dict.

        Raises:
            ValueError: On argument mismatches between 'content' and 'other_nests'
            (e.g. passed nests to a File object)

        Note:
            This is an abstraction for SharePoint objects and should have a wrapper around it.
            In most cases (that I can conceive), it should not be called by itself.
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


def create_content_dict(properties: tuple[str, str, str]) -> dict[str, str]:
    # pylint: disable=C0301
    """
    Creates a content dict with keys 'Name' and 'ServerRelativeUrl'. Meant to be
    called with create_contents or some wrapper function to append its contents to
    the create_contents' output.

    Args:
        properties (tuple): Contains the value of properties of the file/folder.
                            The values of properties each element in the tuple
                              represents, in order, are:
                            1. 'Name'
                            2. 'ServerRelativeUrl'
                            3. 'TimeLastModified'

    Returns:
        A dictionary with keys corresponding to the three properties mentioned above
        and values corresponding to the tuple argument.

        Example:

            create_content_dict('random pte ltd', '/shared_documents', "18 Feb 2026")

        Returns:

            {'Name': 'random pte ltd', 'ServerRelativeUrl': '/shared_documents', 'TimeLastModified': '18 Feb 2026'}
    """

    content_dict = {
        "Name": properties[0],
        "ServerRelativeUrl": properties[1],
        "TimeLastModified": properties[2],
    }
    return content_dict


def create_folder(properties_list: List[tuple[str, str, str]]):
    # pylint: disable=C0301
    """
    Returns an unwrapped folder, similar to what SharePoint's APIResponse's json()
    returns.

    Args:
        properties_list (List[tuple]): A list of properties. Every property is an
                                        individual folder.

    Returns:
        A nested dictionary with layers 'Folders' and 'results'.

        Example:

            create_folder('random pte ltd', '/shared_documents', "18 Feb 2026")

        Returns:

            {'Folders':
                {'results':
                    [{'Name': 'random pte ltd', 'ServerRelativeUrl': '/shared_documents', 'TimeLastModified': '18 Feb 2026'}]
                }
            }
    """

    # create the appropriate dictionaries
    result_value = [
        create_content_dict(folder_property) for folder_property in properties_list
    ]

    # nesting the list of properties in results{}
    result = create_contents("Folders", None, result_value)

    return result
