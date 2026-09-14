import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRAPERS_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "collecte_scrapers"
)

sys.path.insert(0, str(SCRAPERS_DIRECTORY))

import api_sender


class FakeResponse:
    """Simulate a successful response from Odoo."""

    status_code = 200
    text = '{"status": "success", "id": 42}'

    def json(self):
        return {
            "status": "success",
            "id": 42,
        }


class FakeAsyncClient:
    """Record the request sent by api_sender."""

    def __init__(self):
        self.requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exception_type,
        exception,
        traceback,
    ):
        return False

    async def post(self, url, **kwargs):
        self.requests.append(
            {
                "url": url,
                **kwargs,
            }
        )
        return FakeResponse()


class TestBuildOdooPayload(unittest.TestCase):
    """Test validation and construction of Odoo payloads."""

    def test_builds_exact_product_payload(self):
        product_data = {
            "name": "Test product",
            "product_ref": "SHOPIFY-PRODUCT-123",
        }

        payload = api_sender.build_odoo_payload(
            "product",
            product_data,
            api_key="TEST-KEY",
        )

        self.assertEqual(
            payload,
            {
                "api_key": "TEST-KEY",
                "type": "product",
                "data": product_data,
            },
        )

    def test_builds_exact_ad_payload(self):
        ad_data = {
            "ad_ref": "TIKTOK-AD-123",
            "social_network": "tiktok",
            "likes_count": 500,
        }

        payload = api_sender.build_odoo_payload(
            "ad",
            ad_data,
            api_key="TEST-KEY",
        )

        self.assertEqual(payload["api_key"], "TEST-KEY")
        self.assertEqual(payload["type"], "ad")
        self.assertEqual(payload["data"], ad_data)

    def test_missing_api_key_is_rejected(self):
        with patch.dict(
            "os.environ",
            {"ODOO_API_KEY": ""},
            clear=False,
        ):
            with self.assertRaises(ValueError):
                api_sender.build_odoo_payload(
                    "product",
                    {"name": "Test product"},
                    api_key="",
                )

    def test_missing_type_is_rejected(self):
        with self.assertRaises(ValueError):
            api_sender.build_odoo_payload(
                "",
                {"name": "Test product"},
                api_key="TEST-KEY",
            )

    def test_invalid_type_is_rejected(self):
        with self.assertRaises(ValueError):
            api_sender.build_odoo_payload(
                "unknown",
                {"name": "Test product"},
                api_key="TEST-KEY",
            )

    def test_data_must_be_dictionary(self):
        with self.assertRaises(ValueError):
            api_sender.build_odoo_payload(
                "product",
                ["not", "a", "dictionary"],
                api_key="TEST-KEY",
            )


class TestSendToOdoo(unittest.IsolatedAsyncioTestCase):
    """Test the centralized asynchronous HTTP sender."""

    async def test_sends_exact_json_to_odoo(self):
        fake_client = FakeAsyncClient()

        product_data = {
            "name": "Test product",
            "product_ref": "SHOPIFY-PRODUCT-123",
            "category": "Test category",
            "country": "US",
            "source": "scraping",
        }

        with patch.dict(
            "os.environ",
            {
                "ODOO_API_KEY": "TEST-KEY",
                "ODOO_INGEST_URL": (
                    "http://localhost:8069/api/trend/ingest"
                ),
            },
            clear=False,
        ):
            with patch.object(
                api_sender.httpx,
                "AsyncClient",
                return_value=fake_client,
            ):
                result = await api_sender.send_to_odoo(
                    data_type="product",
                    data=product_data,
                )

        self.assertTrue(result)
        self.assertEqual(len(fake_client.requests), 1)

        request = fake_client.requests[0]

        self.assertEqual(
            request["url"],
            "http://localhost:8069/api/trend/ingest",
        )

        self.assertEqual(
            request["json"],
            {
                "api_key": "TEST-KEY",
                "type": "product",
                "data": product_data,
            },
        )

    async def test_missing_key_prevents_network_request(self):
        fake_client = FakeAsyncClient()

        with patch.dict(
            "os.environ",
            {"ODOO_API_KEY": ""},
            clear=False,
        ):
            with patch.object(
                api_sender.httpx,
                "AsyncClient",
                return_value=fake_client,
            ):
                with self.assertRaises(ValueError):
                    await api_sender.send_to_odoo(
                        data_type="product",
                        data={"name": "Test product"},
                    )

        self.assertEqual(fake_client.requests, [])


if __name__ == "__main__":
    unittest.main()