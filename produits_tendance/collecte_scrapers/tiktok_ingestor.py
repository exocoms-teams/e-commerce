import asyncio

from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

TIKTOK_URL = "https://ads.tiktok.com/creative/creativeCenter/trends"

NAVIGATION_TIMEOUT_MS = 30_000


async def scrape_tiktok_trends():
    """Collect trending items from TikTok Creative Center."""

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(
            locale="en-US",
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)

        try:
            print(f"URL value: {TIKTOK_URL}")
            print(f"URL type: {type(TIKTOK_URL)}")

            response = await page.goto(
                TIKTOK_URL,
                wait_until="domcontentloaded",
                timeout=NAVIGATION_TIMEOUT_MS,
            )

            print(f"Final URL: {page.url}")
            print(f"Page title: {await page.title()}")

            if response is None:
                print("Tiktok returned no HTTP response.")
                return []
            print( f"HTTP status: {response.status}")
            if response.status >= 400:
                print(f"TikTok refused the request with HTTP {response.status}.")
                await page.screenshot(
                path="tiktok_error.png",
                    full_page=True,
        )
            return []

            print("TikTok Creative Center loaded successfully.")
            return []

        except PlaywrightTimeoutError:
            print("TikTok did not load within 30 seconds.")
            return []

        except Exception as error:
            print(f"TikTok navigation failed: {error}")
            return []

        finally:
            await context.close()
            await browser.close()


def build_ad_payload(item, api_key):
    """Convert a TikTok result to the Odoo ad contract."""
    ...


async def push_to_odoo(payload):
    """Send one ad payload to the Odoo ingestion endpoint."""
    ...


async def main():
    print("Starting TikTok scraper...")

    items = await scrape_tiktok_trends()

    print(f"Number of collected items: {len(items)}")


if __name__ == "__main__":
    asyncio.run(main())