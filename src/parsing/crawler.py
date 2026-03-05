import asyncio
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme:
        return url
    return f"https://{url}"


async def fetch_page(url: str) -> str:
    target_url = _normalize_url(url)
    return await asyncio.to_thread(_fetch_page_sync, target_url)


def _fetch_page_sync(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
        content = page.content()
        browser.close()
        return content
