import asyncio
import hashlib
import json
import os
import httpx

from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


TIKTOK_URL_TEMPLATE = (
    "https://ads.tiktok.com/business/creativecenter/"
    "inspiration/topads/pc/en?region={region}&period=30"
)

NAVIGATION_TIMEOUT_MS = 30_000


def parse_compact_number(value):
    """Convert TikTok values such as 2K and 25K into integers."""

    if not value:
        raise ValueError("TikTok count is empty.")

    normalized_value = value.strip().upper().replace(",", "")

    if not normalized_value:
        raise ValueError("TikTok count is empty.")

    multipliers = {
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000,
    }

    suffix = normalized_value[-1]

    if suffix in multipliers:
        number = float(normalized_value[:-1])
        return int(number * multipliers[suffix])

    return int(float(normalized_value))


async def extract_visible_ads(page, region):
    """Extract the public Top Ads currently displayed by TikTok."""

    analytics_buttons = page.get_by_text(
        "See analytics",
        exact=True,
    )

    number_of_ads = await analytics_buttons.count()

    print(f"Number of visible ads: {number_of_ads}")

    items = []

    for index in range(number_of_ads):
        analytics_button = analytics_buttons.nth(index)

        # The complete advertisement card is three parents above the button.
        card = analytics_button.locator("xpath=../../..")
        card_text = await card.inner_text()

        # Temporary inspection of links inside this card.
        card_links = await card.locator("[href]").evaluate_all(
            """
            elements => elements.map(element => ({
                text: element.innerText,
                href: element.href
            }))
            """
        )

        if not card_links:
            print(f"Ad {index + 1} has no analytics URL.")
            continue

        snapshot_url = card_links[0]["href"]
        ad_id = snapshot_url.rstrip("/").split("/")[-1]

        lines = [
            line.strip()
            for line in card_text.splitlines()
            if line.strip()
        ]

        try:
            likes_label_index = lines.index("Likes")
            likes_text = lines[likes_label_index - 1]
            likes_count = parse_compact_number(likes_text)

            descriptive_lines = lines[:likes_label_index - 1]

            objective = (
                descriptive_lines[0]
                if descriptive_lines
                else "Unknown"
            )

            product_name = (
                descriptive_lines[-1]
                if descriptive_lines
                else f"TikTok Ad {index + 1}"
            )

            item = {
                "ad_id": ad_id,
                "product_name": product_name,
                "objective": objective,
                "likes_count": likes_count,
                "region": region,
                  "snapshot_url": snapshot_url,
            }

            items.append(item)

        except (ValueError, TypeError, IndexError) as error:
            print(f"Could not parse ad {index + 1}: {error}")
            print(f"Card content: {lines}")

    # Return only after every advertisement has been inspected.
    return items

async def scrape_tiktok_trends():
    """Collect trending items from TikTok Creative Center."""

    regions = ["US", "FR"]
    all_items = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
        )

        context = await browser.new_context(
            locale="en-US",
            viewport={"width": 1440, "height": 900},
        )

        page = await context.new_page()

        page.set_default_navigation_timeout(
            NAVIGATION_TIMEOUT_MS
        )

        try:
            for region in regions:
                url = TIKTOK_URL_TEMPLATE.format(
                    region=region
                )

                print(
                    f"\nCollecting TikTok ads "
                    f"for region: {region}"
                )

                response = await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=NAVIGATION_TIMEOUT_MS,
                )

                if response is None:
                    print(
                        f"No HTTP response for region: "
                        f"{region}"
                    )
                    continue

                print(f"Final URL: {page.url}")
                print(f"HTTP status: {response.status}")

                if response.status >= 400:
                    print(
                        f"TikTok refused region {region} "
                        f"with HTTP {response.status}."
                    )
                    continue

                # Give TikTok time to display the advertisement cards.
                await page.wait_for_timeout(5_000)

                region_items = await extract_visible_ads(
                    page,
                    region=region,
                )

                all_items.extend(region_items)

            # This section is outside the region loop.
            print("\n--- EXTRACTED ADS ---")
            unique_items_by_id = {
                item["ad_id"]: item
                for item in all_items
            }

            all_items = list(unique_items_by_id.values())


            for item in all_items:
                print(item)

            print("--- END EXTRACTED ADS ---\n")

            return all_items

        except PlaywrightTimeoutError:
            print("TikTok did not load within 30 seconds.")
            return all_items

        except Exception as error:
            print(f"TikTok scraping failed: {error}")
            return all_items

        finally:
            await context.close()
            await browser.close()


def build_ad_payload(item, api_key):
    """Convert one extracted TikTok advertisement to the Odoo contract."""

    product_identity = item["product_name"].strip().lower()

    product_hash = hashlib.sha256(
        product_identity.encode("utf-8")
    ).hexdigest()[:16].upper()

    return {
        "api_key": api_key,
        "type": "ad",
        "data": {
            "ad_ref": f"TIKTOK-AD-{item['ad_id']}",
            "product_ref": f"TIKTOK-PRODUCT-{product_hash}",
            "product_name": item["product_name"],
            "country": item["region"],
            "social_network": "tiktok",
            "likes_count": item["likes_count"],
            "shares_count": 0,
            "snapshot_url": item["snapshot_url"],
            "platforms": "tiktok",
            "is_active": True,
        },
    }


async def push_to_odoo(client, odoo_url, payload):
    """Send one TikTok advertisement payload to Odoo."""

    try:
        response = await client.post(
            odoo_url,
            json=payload,
        )

        if response.status_code != 200:
            print(
                f"Odoo rejected {payload['data']['ad_ref']}: "
                f"HTTP {response.status_code} - {response.text}"
            )
            return False

        result = response.json()

        if result.get("status") != "success":
            print(
                f"Odoo returned an error for "
                f"{payload['data']['ad_ref']}: {result}"
            )
            return False

        print(
            f"Inserted {payload['data']['ad_ref']} "
            f"with Odoo ID {result.get('id')}"
        )

        return True

    except httpx.TimeoutException:
        print(
            f"Odoo request timed out for "
            f"{payload['data']['ad_ref']}"
        )
        return False

    except httpx.RequestError as error:
        print(f"Could not connect to Odoo: {error}")
        return False

    except ValueError:
        print(f"Odoo returned invalid JSON: {response.text}")
        return False


async def main():
    print("Starting TikTok scraper...")

    items = await scrape_tiktok_trends()

    print(f"Number of collected items: {len(items)}")

    if len(items) < 5:
        print("Not enough TikTok ads were collected.")
        return

    api_key = os.getenv("ODOO_API_KEY")

    odoo_url = os.getenv(
        "ODOO_INGEST_URL",
        "http://localhost:8069/api/trend/ingest",
    )

    if not api_key:
        print("ODOO_API_KEY is not configured.")
        return

    payloads = [
        build_ad_payload(item, api_key)
        for item in items
    ]

    print(f"Number of generated payloads: {len(payloads)}")

    successful_insertions = 0

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(15.0)
    ) as client:
        for payload in payloads:
            success = await push_to_odoo(
                client,
                odoo_url,
                payload,
            )

            if success:
                successful_insertions += 1

    print(
        f"Successfully injected "
        f"{successful_insertions}/{len(payloads)} "
        f"ads into Odoo."
    )


if __name__ == "__main__":
    asyncio.run(main())