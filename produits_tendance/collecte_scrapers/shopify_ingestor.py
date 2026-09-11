import asyncio
import os
from urllib.parse import urlparse
from decimal import Decimal, InvalidOperation
import json
import httpx

HTTP_TIMEOUT_SECONDS = 15.0
SHOPIFY_PRODUCT_LIMIT = 20



def normalize_shop_url(shop_url):
    """Validate and normalize a Shopify store URL."""

    if not shop_url:
        raise ValueError("The Shopify store URL is missing.")

    normalized_url = shop_url.strip().rstrip("/")
    parsed_url = urlparse(normalized_url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError(
            "The Shopify store URL must begin with http:// or https://."
        )

    if not parsed_url.netloc:
        raise ValueError("The Shopify store URL has no valid domain.")

    return normalized_url


async def fetch_shopify_products(shop_url):
    """Retrieve products from a public Shopify catalogue."""

    try:
        normalized_shop_url = normalize_shop_url(shop_url)
    except ValueError as error:
        print(f"Invalid Shopify URL: {error}")
        return []

    products_url = f"{normalized_shop_url}/products.json"

    print(f"Requesting Shopify catalogue: {products_url}")

    try:
        async with httpx.AsyncClient(
            timeout=HTTP_TIMEOUT_SECONDS,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                products_url,
                params={"limit": SHOPIFY_PRODUCT_LIMIT},
                headers={
                    "Accept": "application/json",
                    "User-Agent": "produits-tendance-shopify-ingestor/1.0",
                },
            )

    except httpx.TimeoutException:
        print(
            f"Shopify did not respond within "
            f"{HTTP_TIMEOUT_SECONDS} seconds."
        )
        return []

    except httpx.RequestError as error:
        print(f"Could not connect to Shopify: {error}")
        return []

    if response.status_code == 403:
        print("The Shopify store refused access to its product catalogue.")
        return []

    if response.status_code == 404:
        print("The Shopify store does not expose /products.json publicly.")
        return []

    if response.status_code == 429:
        print("Shopify rate limit reached. Please try again later.")
        return []

    if response.status_code >= 500:
        print(
            f"Shopify server error: HTTP {response.status_code}."
        )
        return []

    if response.status_code >= 400:
        print(
            f"Shopify request failed: HTTP {response.status_code}."
        )
        return []

    try:
        response_data = response.json()
    except ValueError:
        print("Shopify returned invalid JSON.")
        return []

    products = response_data.get("products")

    if not isinstance(products, list):
        print("The Shopify response does not contain a product list.")
        return []

    print(f"Number of Shopify products collected: {len(products)}")

    return products



def parse_shopify_product(product, shop_url):
    """Convert one Shopify product into normalized product data."""

    if not isinstance(product, dict):
        raise ValueError("The Shopify product must be a dictionary.")

    product_id = product.get("id")
    product_name = str(product.get("title") or "").strip()
    handle = str(product.get("handle") or "").strip()

    if not product_id:
        raise ValueError("The Shopify product has no ID.")

    if not product_name:
        raise ValueError("The Shopify product has no title.")

    normalized_shop_url = normalize_shop_url(shop_url)

    variants = product.get("variants") or []
    valid_prices = []

    for variant in variants:
        price_value = variant.get("price")

        if price_value in (None, ""):
            continue

        try:
            valid_prices.append(Decimal(str(price_value)))
        except (InvalidOperation, ValueError, TypeError):
            continue

    price = min(valid_prices) if valid_prices else Decimal("0")

    image_url = ""

    primary_image = product.get("image")

    if isinstance(primary_image, dict):
        image_url = str(primary_image.get("src") or "").strip()

    if not image_url:
        images = product.get("images") or []

        if images and isinstance(images[0], dict):
            image_url = str(images[0].get("src") or "").strip()

    product_url = ""

    if handle:
        product_url = f"{normalized_shop_url}/products/{handle}"

    is_available = any(
        bool(variant.get("available"))
        for variant in variants
        if isinstance(variant, dict)
    )

    return {
        "shopify_id": str(product_id),
        "product_ref": f"SHOPIFY-PRODUCT-{product_id}",
        "product_name": product_name,
        "vendor": str(product.get("vendor") or "").strip(),
        "category": str(product.get("product_type") or "").strip(),
        "price": float(price),
        "product_url": product_url,
        "image_url": image_url,
        "is_active": is_available,
    }

def build_product_payload(product, api_key, country):
    """Bsuild the exact Odoo product payload."""

    if not api_key:
        raise ValueError("The Odoo API key is missing.")

    if not country:
        raise ValueError(
            "The Shopify product country is missing."
        )

    if not product.get("product_ref"):
        raise ValueError(
            "The parsed product has no product_ref."
        )

    if not product.get("product_name"):
        raise ValueError(
            "The parsed product has no product_name."
        )

    return {
        "api_key": api_key,
        "type": "product",
        "data": {
            "name": product["product_name"],
            "product_ref": product["product_ref"],
            "category": (
                product.get("category")
                or "Uncategorized"
            ),
            "country": country.strip().upper(),
            "source": "scraping",
            "sales_count": 0,
            "image_url": (
                product.get("image_url") or None
            ),
            "price": product.get("price", 0.0),
        },
    }


async def push_to_odoo(payload, ingest_url):
    """Send one Shopify product payload to Odoo."""

    product_ref = payload.get(
        "data",
        {},
    ).get(
        "product_ref",
        "unknown-product",
    )

    try:
        async with httpx.AsyncClient(
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as client:
            response = await client.post(
                ingest_url,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )

    except httpx.TimeoutException:
        print(
            f"Odoo request timed out for {product_ref}."
        )
        return False

    except httpx.RequestError as error:
        print(
            f"Could not connect to Odoo for "
            f"{product_ref}: {error}"
        )
        return False

    try:
        response_data = response.json()
    except ValueError:
        response_data = {}

    if response.status_code >= 400:
        error_message = (
            response_data
            if response_data
            else response.text
        )

        print(
            f"Odoo rejected {product_ref}: "
            f"HTTP {response.status_code} - "
            f"{error_message}"
        )
        return False

    if response_data.get("status") != "success":
        print(
            f"Odoo returned an unexpected response "
            f"for {product_ref}: {response_data}"
        )
        return False

    print(
        f"Synchronized {product_ref} "
        f"with Odoo ID {response_data.get('id')}"
    )

    return True


async def main():
    """Collect and synchronize Shopify products."""

    print("Starting Shopify ingestor...")

    shop_url = os.getenv("SHOPIFY_STORE_URL")
    api_key = os.getenv("ODOO_API_KEY")
    country = os.getenv("SHOPIFY_COUNTRY")
    ingest_url = os.getenv(
        "ODOO_INGEST_URL",
        "http://localhost:8069/api/trend/ingest",
    )

    if not shop_url:
        print(
            "Missing SHOPIFY_STORE_URL "
            "environment variable."
        )
        return

    if not api_key:
        print(
            "Missing ODOO_API_KEY "
            "environment variable."
        )
        return

    if not country:
        print(
            "Missing SHOPIFY_COUNTRY "
            "environment variable."
        )
        return

    raw_products = await fetch_shopify_products(
        shop_url
    )

    parsed_products = []

    for index, raw_product in enumerate(
        raw_products
    ):
        try:
            parsed_product = parse_shopify_product(
                raw_product,
                shop_url,
            )
            parsed_products.append(parsed_product)

        except ValueError as error:
            print(
                f"Could not parse Shopify product "
                f"{index + 1}: {error}"
            )

    print(
        f"Number of parsed Shopify products: "
        f"{len(parsed_products)}"
    )

    payloads = []

    for index, product in enumerate(
        parsed_products
    ):
        try:
            payload = build_product_payload(
                product,
                api_key,
                country,
            )
            payloads.append(payload)

        except ValueError as error:
            print(
                f"Could not build payload "
                f"{index + 1}: {error}"
            )

    print(
        f"Number of generated payloads: "
        f"{len(payloads)}"
    )

    if payloads:
        safe_payload = {
            **payloads[0],
            "api_key": "***",
        }

        print("\n--- FIRST ODOO PRODUCT PAYLOAD ---")
        print(
            json.dumps(
                safe_payload,
                indent=2,
                ensure_ascii=False,
            )
        )
        print("--- END FIRST ODOO PRODUCT PAYLOAD ---")

    successful_injections = 0

    for payload in payloads:
        success = await push_to_odoo(
            payload,
            ingest_url,
        )

        if success:
            successful_injections += 1

    print(
        f"Successfully synchronized "
        f"{successful_injections}/{len(payloads)} "
        f"Shopify products with Odoo."
    )


if __name__ == "__main__":
    asyncio.run(main())