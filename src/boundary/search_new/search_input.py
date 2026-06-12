"""
This module isolates everything related to manual input.
"""

from core.individual import Individual, sort_individuals
from typing import List
from playwright.async_api import Page
import logging
import asyncio


def set_individual_attributes(kah_list: List[Individual]) -> List[Individual]:
    """
    This function relies on user input to mutate/set individual attributes of
    the list of individuals passed to it.
    """

    kah_list = sort_individuals(kah_list)

    for individual in kah_list:
        print(f"Individual: {individual.name},\n ID: {individual.id_value}")
        individual.id_type = input("Enter id type: ")
        individual.id_status = input("Enter id status: ")
        individual.chinese_name = input("Enter chinese name ('-') if none: ")
        if individual.chinese_name != "-":
            individual.baidu = True
        else:
            while True:
                is_baidu = input("Baidu search? (Y/N): ")
                if is_baidu.upper() == "Y":
                    individual.baidu = True
                    break
                elif is_baidu.upper() == "N":
                    individual.baidu = False
                    break
                else:
                    print("Invalid input")

    return kah_list


def append_related_individuals(kah_list: List[Individual]) -> List[Individual]:
    """
    This function appends individuals with the 'RELATED' role to kah_list
    """

    while True:
        is_new_individual = input("Any other related individuals? (Y/N): ")
        if is_new_individual.upper() == "Y":
            new_individual = Individual(
                "-", "-", "-", "-", "-", True, True, False, "RELATED"
            )
            new_individual.name = input("Enter related party name: ")
            new_individual.chinese_name = input(
                f"Enter {new_individual.name}'s chinese name ('-' if None): "
            )
            if new_individual.chinese_name != "-":
                new_individual.baidu = True
            else:
                while True:
                    is_baidu = input("Baidu search? (Y/N): ")
                    if is_baidu.upper() == "Y":
                        new_individual.baidu = True
                        break
                    elif is_baidu.upper() == "N":
                        new_individual.baidu = False
                        break
                    else:
                        print("Invalid input")
            kah_list.append(new_individual)
        if is_new_individual.upper() == "N":
            break
        else:
            print("Invalid input")
    return kah_list


def get_screenshot_name(result: tuple[str, str, Page]) -> str:
    """
    Returns the name of the screenshot from a tuple 'result'.
    """

    name = None
    if result[0] == "Google":
        name = f"{result[1]} - Google Search"
    if result[0] == "Baidu":
        name = f"{result[1]}_百度搜索"
    if name is None:
        raise ValueError(
            "Tuple passed to get_screenshot_name is neither Google nor Baidu!"
        )

    return name


async def async_input(prompt: str) -> str:
    """
    Emulates 'input()' for async functions.
    """
    return await asyncio.to_thread(input, prompt)


async def screenshot_individual_search(
    search_results: dict[Individual, List[tuple[str, str, Page]]],
) -> dict[Individual, dict[str, bytes]]:
    """
    Relies on user input to verify, then screenshot individual search queries from
    the input list.

    Args:
        searches(dict[str, List[tuple]]): A dictionary that maps an individual to his/her
                                            list of search results (in tuples). Should be
                                            passed to directly from load_pages_for_individual.

    Returns:
    {Individual: {screenshot_name: screenshot_bytes}}

    Note:
        Each verification triggers a screenshot, there would be no point in separating
        input/screenshots.

        This function has to be async because it receives an async page object, but it is
        functionally sync.
    """

    # precondition: input has one key (one individual)
    if len(search_results) != 1:
        logging.error(
            "Expected one individual to be passed to screenshot_individual_search,"
            " but received %s",
            search_results,
        )
        raise ValueError("More than one item passed to screenshot_individual_search")

    individual = next(iter(search_results))
    individual_searches = search_results[individual]

    # what we aim to output
    individual_dict = {}

    # verify the pages one by one
    for individual_search in individual_searches:
        await individual_search[2].bring_to_front()
        # wait for user input
        while True:
            kyc_ok = await async_input("KYC ok? (Y/N): ")

            if kyc_ok.upper() == "Y":
                individual.kyc_status = True
                break
            if kyc_ok.upper() == "N":
                individual.kyc_status = False
                break
            print("Invalid input")

        # get screenshot name
        scrnshot_name = get_screenshot_name(individual_search)
        # screenshot
        scrnshot_bytes = await individual_search[2].screenshot(full_page=True)

        individual_dict[scrnshot_name] = scrnshot_bytes

    return {individual: individual_dict}
