"""
This module orchestrates the search process.
Manages sync and async functions.
"""

import asyncio
import random
from typing import List

from playwright.async_api import BrowserContext, Page

from boundary.search_new.browser_init import init_browser
from boundary.search_new.concurrent_loading import load_pages_for_individual
from boundary.search_new.search_input import (
    append_related_individuals,
    screenshot_individual_search,
    set_individual_attributes,
)
from core.individual import Individual


async def search_orchestrator(
    kah_list: List[Individual],
) -> tuple[List[dict[str, dict[str, bytes]]], List[Individual]]:
    """
    Orchestrates the search process using helper modules.
    Returns a list of dicts for backwards compatibility with search.py.
    Rewrite if you have time.
    """

    kah_list = set_individual_attributes(kah_list)
    kah_list = append_related_individuals(kah_list)

    page, context = await init_browser()
    page: Page
    context: BrowserContext

    tasks = []
    for individual in kah_list:
        tasks.append(load_pages_for_individual(page, individual))
        await asyncio.sleep(random.uniform(0.5, 1.5))  # noqa: S311

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
    return output_wrapper, kah_list
