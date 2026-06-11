"""
This module orchestrates the search process.
Manages sync and async functions.
"""

from boundary.search_new.browser_init import init_browser
from core.individual import Individual
from boundary.search_new.concurrent_loading import load_pages_for_individual
from boundary.search_new.search_input import (
    set_individual_attributes,
    screenshot_individual_search,
)
from playwright.async_api import Page, BrowserContext
import asyncio
from typing import List


async def search_orchestrator(
    kah_list: List[Individual],
) -> List[dict[str, dict[str, bytes]]]:
    """
    Orchestrates the search process using helper modules.
    Returns a list of dicts for backwards compatibility with search.py.
    Rewrite if you have time.
    """

    kah_list = set_individual_attributes(kah_list)

    page, context = await init_browser()
    page: Page
    context: BrowserContext

    tasks = [load_pages_for_individual(page, individual) for individual in kah_list]

    # thank god for type hint diligence
    search_results: List[List[tuple[str, str, Page]]] = await asyncio.gather(*tasks)

    output: dict[str, dict[str, bytes]] = {}
    output_wrapper = []

    for individual, search_result in zip(kah_list, search_results):
        screenshots = await screenshot_individual_search({individual: search_result})
        # get the individual, he's the only key in the dict
        individual = next(iter(screenshots))
        # assign the bytes to the output
        # initialize
        output[individual.name] = {}
        for name_bytes in screenshots[individual].items():
            # name_bytes is a tuple
            output[individual.name][name_bytes[0]] = name_bytes[1]
        output_wrapper.append(output)

    await context.close()
    return output_wrapper
