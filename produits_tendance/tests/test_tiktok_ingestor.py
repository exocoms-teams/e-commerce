import sys
import unittest
from pathlib import Path


SCRAPER_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "collecte_scrapers"
)

sys.path.insert(0, str(SCRAPER_DIRECTORY))

from tiktok_ingestor import build_ad_payload, parse_compact_number


class TestParseCompactNumber(unittest.TestCase):

    def test_plain_number(self):
        self.assertEqual(parse_compact_number("13"), 13)

    def test_thousands(self):
        self.assertEqual(parse_compact_number("2K"), 2_000)

    def test_decimal_thousands(self):
        self.assertEqual(parse_compact_number("1.5K"), 1_500)

    def test_millions(self):
        self.assertEqual(parse_compact_number("2.5M"), 2_500_000)

    def test_number_with_comma(self):
        self.assertEqual(parse_compact_number("1,250"), 1_250)

    def test_empty_value_raises_error(self):
        with self.assertRaises(ValueError):
            parse_compact_number("")


class TestBuildAdPayload(unittest.TestCase):

    def setUp(self):
        self.item = {
            "ad_id": "7662006149396824084",
            "product_name": "Medicine",
            "objective": "Video Views",
            "likes_count": 6_000,
            "region": "US",
            "snapshot_url": (
                "https://ads.tiktok.com/business/"
                "creativecenter/topads/7662006149396824084"
            ),
        }

    def test_payload_uses_ad_contract(self):
        payload = build_ad_payload(
            self.item,
            api_key="test-key",
        )

        self.assertEqual(payload["api_key"], "test-key")
        self.assertEqual(payload["type"], "ad")
        self.assertEqual(
            payload["data"]["social_network"],
            "tiktok",
        )
        self.assertEqual(
            payload["data"]["likes_count"],
            6_000,
        )
        self.assertEqual(
            payload["data"]["country"],
            "US",
        )

    def test_payload_uses_real_tiktok_id(self):
        payload = build_ad_payload(
            self.item,
            api_key="test-key",
        )

        self.assertEqual(
            payload["data"]["ad_ref"],
            "TIKTOK-AD-7662006149396824084",
        )

    def test_payload_contains_source_url(self):
        payload = build_ad_payload(
            self.item,
            api_key="test-key",
        )

        self.assertEqual(
            payload["data"]["snapshot_url"],
            self.item["snapshot_url"],
        )

    def test_product_reference_is_stable(self):
        first_payload = build_ad_payload(
            self.item,
            api_key="first-key",
        )

        second_item = {
            **self.item,
            "likes_count": 10_000,
        }

        second_payload = build_ad_payload(
            second_item,
            api_key="second-key",
        )

        self.assertEqual(
            first_payload["data"]["product_ref"],
            second_payload["data"]["product_ref"],
        )


if __name__ == "__main__":
    unittest.main()