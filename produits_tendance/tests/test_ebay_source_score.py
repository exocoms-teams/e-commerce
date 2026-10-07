import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRAPERS_DIR = (
    Path(__file__).resolve().parents[1] / "collecte_scrapers"
)
sys.path.insert(0, str(SCRAPERS_DIR))

import ebay_ingestor


class TestEbaySourceScore(unittest.TestCase):

    def test_feedback_count_is_not_sent_as_source_rating(self):
        for feedback_score in (0, 5, 100, 25000):
            with self.subTest(feedback_score=feedback_score):
                item = {
                    "itemId": "EBAY-AUDIT-123",
                    "title": "Source score audit product",
                    "seller": {"feedbackScore": feedback_score},
                    "price": {"value": "25.50"},
                    "itemLocation": {"country": "FR"},
                }

                with patch.object(
                    ebay_ingestor,
                    "send_to_odoo_sync",
                    return_value=True,
                ) as sender:
                    result = ebay_ingestor.push_to_odoo(
                        item,
                        "http://localhost:8069/api/trend/ingest",
                        "TEST-KEY",
                    )

                self.assertTrue(result)
                sender.assert_called_once()

                arguments = sender.call_args.kwargs
                data = arguments["data"]

                self.assertEqual(arguments["data_type"], "product")
                self.assertEqual(arguments["api_key"], "TEST-KEY")
                self.assertEqual(data["product_ref"], "EBAY-AUDIT-123")
                self.assertEqual(data["source"], "api")
                self.assertAlmostEqual(data["price"], 25.50)
                self.assertNotIn("score_site_x", data)


if __name__ == "__main__":
    unittest.main()