"""
To execute the searches, we activate another headed browser instance.
To load all pages concurrently, we use an async instance of
playwright (or technically, cloakbrowser).
"""

from cloakbrowser import launch_async
from playwright.async_api import Page, BrowserContext


async def init_browser() -> tuple[Page, BrowserContext]:
    """
    Initializes an async browser for KYC checks.

    Returns:
        A tuple (page, context)
    """
    browser = await launch_async(
        # channel="msedge",
        headless=False,
        args=[
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1920,1080",
            "--window-position=1,1",
            "--start-maximized",
        ],
    )

    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        device_scale_factor=2,
    )

    page = context.pages[0] if context.pages else await context.new_page()
    for p in context.pages[1:]:
        await p.close()

    return page, context
