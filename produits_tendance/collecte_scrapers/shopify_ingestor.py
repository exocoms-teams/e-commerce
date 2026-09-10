
import asyncio
import os
from urllib.parse import urlparse
from decimal import Decimal, InvalidOperation

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

def build_product_payload(product, api_key):
    """Build the exact Odoo payload with type='product'."""

async def push_to_odoo(payload, ingest_url):
    """POST one product to the internal Odoo endpoint."""



async def main():
    """Collect and parse Shopify products."""

    shop_url = os.getenv("SHOPIFY_STORE_URL")

    if not shop_url:
        print("Missing SHOPIFY_STORE_URL environment variable.")
        return

    raw_products = await fetch_shopify_products(shop_url)
    parsed_products = []

    for index, raw_product in enumerate(raw_products):
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

    if parsed_products:
        print("\n--- FIRST PARSED SHOPIFY PRODUCT ---")

        for key, value in parsed_products[0].items():
            print(f"{key}: {value}")

        print("--- END FIRST PARSED SHOPIFY PRODUCT ---")


if __name__ == "__main__":
    asyncio.run(main())