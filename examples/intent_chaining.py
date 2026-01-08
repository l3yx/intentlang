import asyncio
from intentlang import Intent
from playwright.async_api import async_playwright, Page


async def test():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    url = "https://l3yx.github.io/"

    intent_a = (
        Intent()
        .goal("Open the url")
        .input(
            # Format: name=(value, "description")
            url=(url, "Target URL to open")
        )
        .tools([
            # Formats: function, or (object, "name", "description")
            (context, "context", "Playwright Context instance (async API)")
        ])
        .output(
            # Format: name=(type, "description")
            page=(Page, "Playwright Page instance")
        )
    )
    page = (await intent_a.run()).output.page
    print(page)

    intent_b = (
        Intent()
        .goal("Get webpage title")
        .input(
            # Format: (value, "description")
            page=(page, "Playwright Page instance")
        )
        .output(
            # Format: (type, "description")
            title=(str, "Webpage title")
        )
    )
    title = (await intent_b.run()).output.title
    print(title)

asyncio.run(test())
