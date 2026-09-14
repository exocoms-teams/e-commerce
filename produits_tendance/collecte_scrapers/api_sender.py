"""Common utility for sending collected data to Odoo."""

import os
from urllib.parse import urlparse

import httpx


DEFAULT_ODOO_URL = (
    "http://localhost:8069/api/trend/ingest"
)
HTTP_TIMEOUT_SECONDS = 15.0
VALID_DATA_TYPES = {"product", "ad", "score"}


def build_odoo_payload(
    data_type,
    data,
    api_key=None,
):
    """Validate input and build the exact Odoo payload."""

    resolved_api_key = (
        api_key or os.getenv("ODOO_API_KEY")
    )

    if not resolved_api_key:
        raise ValueError(
            "ODOO_API_KEY is missing."
        )

    if not isinstance(data_type, str):
        raise ValueError(
            "The data type must be a string."
        )

    normalized_type = data_type.strip().lower()

    if not normalized_type:
        raise ValueError(
            "The data type is missing."
        )

    if normalized_type not in VALID_DATA_TYPES:
        raise ValueError(
            f"Unsupported data type: {normalized_type}."
        )

    if not isinstance(data, dict):
        raise ValueError(
            "The data must be a Python dictionary."
        )

    if not data:
        raise ValueError(
            "The data dictionary cannot be empty."
        )

    return {
        "api_key": resolved_api_key,
        "type": normalized_type,
        "data": data,
    }


def get_odoo_url(odoo_url=None):
    """Validate and return the Odoo ingestion URL."""

    resolved_url = (
        odoo_url
        or os.getenv("ODOO_INGEST_URL")
        or DEFAULT_ODOO_URL
    )

    parsed_url = urlparse(resolved_url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError(
            "The Odoo URL must begin with "
            "http:// or https://."
        )

    if not parsed_url.netloc:
        raise ValueError(
            "The Odoo URL has no valid domain."
        )

    return resolved_url


def _record_reference(data):
    """Return a useful record reference for logs."""

    return (
        data.get("product_ref")
        or data.get("ad_ref")
        or data.get("score_ref")
        or "unknown-record"
    )


def _handle_response(response, data):
    """Validate an Odoo HTTP response."""

    reference = _record_reference(data)

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
            f"Odoo rejected {reference}: "
            f"HTTP {response.status_code} - "
            f"{error_message}"
        )
        return False

    if response_data.get("status") != "success":
        print(
            "Odoo returned an unexpected response "
            f"for {reference}: {response_data}"
        )
        return False

    print(
        f"Synchronized {reference} "
        f"with Odoo ID {response_data.get('id')}"
    )

    return True


async def send_to_odoo(
    data_type,
    data,
    api_key=None,
    odoo_url=None,
    client=None,
):
    """Asynchronously send collected data to Odoo."""

    payload = build_odoo_payload(
        data_type,
        data,
        api_key,
    )
    resolved_url = get_odoo_url(odoo_url)
    reference = _record_reference(data)

    try:
        if client is not None:
            response = await client.post(
                resolved_url,
                json=payload,
            )
        else:
            async with httpx.AsyncClient(
                timeout=HTTP_TIMEOUT_SECONDS,
            ) as async_client:
                response = await async_client.post(
                    resolved_url,
                    json=payload,
                )

    except httpx.TimeoutException:
        print(
            f"Odoo request timed out for {reference}."
        )
        return False

    except httpx.RequestError as error:
        print(
            f"Could not connect to Odoo for "
            f"{reference}: {error}"
        )
        return False

    return _handle_response(response, data)


def send_to_odoo_sync(
    data_type,
    data,
    api_key=None,
    odoo_url=None,
):
    """Synchronously send collected data to Odoo."""

    payload = build_odoo_payload(
        data_type,
        data,
        api_key,
    )
    resolved_url = get_odoo_url(odoo_url)
    reference = _record_reference(data)

    try:
        with httpx.Client(
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as client:
            response = client.post(
                resolved_url,
                json=payload,
            )

    except httpx.TimeoutException:
        print(
            f"Odoo request timed out for {reference}."
        )
        return False

    except httpx.RequestError as error:
        print(
            f"Could not connect to Odoo for "
            f"{reference}: {error}"
        )
        return False

    return _handle_response(response, data)