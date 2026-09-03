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
        browser = await playwright.firefox.launch(
            headless=False,
        )

        context = await browser.new_context(
            locale="en-US",
            viewport={"width": 1440, "height": 900},
        )

        page = await context.new_page()
        page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)

        try:
            response = await page.goto(
                TIKTOK_URL,
                wait_until="domcontentloaded",
                timeout=NAVIGATION_TIMEOUT_MS,
            )

            if response is None:
                print("TikTok returned no HTTP response.")
                return []

            print(f"Final URL: {page.url}")
            print(f"HTTP status: {response.status}")

            if response.status >= 400:
                print(f"TikTok refused the request with HTTP {response.status}.")
                return []

            print(f"Page title: {await page.title()}")
            print("TikTok Creative Center loaded successfully.")

            # Give the JavaScript content time to appear.
            await page.wait_for_timeout(5_000)

            body_text = await page.locator("body").inner_text()

            print("\n--- PAGE CONTENT ---")
            print(body_text[:5_000])
            print("--- END PAGE CONTENT ---\n")

            await page.screenshot(
                path="tiktok_trends.png",
                full_page=True,
            )
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