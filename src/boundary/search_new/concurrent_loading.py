"""
This module loads pages concurrently.
"""

from playwright.async_api import Page
from core.individual import Individual
from typing import Literal
import asyncio


def load_pages_for_individual(page: Page, individual: Individual):
    """
    Loads pages concurrently using load_page.

    Returns:
            A coroutine that returns a list of tuples containing:
                A tuple containing the search's:
                    1. engine
                    2. query
                    3. page
    """

    tasks = []
    tasks.append(load_page(page.context, "Google", individual.name))
    if individual.baidu is True:
        tasks.append(load_page(page.context, "Baidu", individual.name))
        if individual.chinese_name != "-":
            tasks.append(load_page(page.context, "Google", individual.chinese_name))
            tasks.append(load_page(page.context, "Baidu", individual.chinese_name))

    # return coroutine even though it hasn't finished loading yet
    loaded_pages = asyncio.gather(*tasks)  # note that * is NOT A POINTER IN PYTHON

    return loaded_pages


async def load_page(context, engine: Literal["Google", "Baidu"], query: str) -> tuple:
    """
    Creates a new page, navigates to the query using the appropriate search engine

    Args:
        context: The browser context used to open a new page
        engine(Literal): Selects the search engine from either "Google" or "Baidu"
        query: The query to be searched for in the search bar

    Returns:
        A tuple containing the search's:
            1. engine
            2. query
            3. page
    """

    page = await context.new_page()
    if engine == "Google":
        await page.goto(f"https://google.com/search?q={query}")
    elif engine == "Baidu":
        await page.goto(f"https://www.baidu.com/s?wd={query}", timeout=60000)

    return (engine, query, page)
