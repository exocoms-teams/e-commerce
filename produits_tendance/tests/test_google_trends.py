from datetime import datetime
from unittest.mock import patch

import pandas as pd

from odoo.tests.common import TransactionCase
from odoo.addons.produits_tendance.services import (
    google_trends,
    scoring_orchestrator,
)


class TestGoogleTrends(TransactionCase):

    def setUp(self):
        super().setUp()

        self.scoring_time = datetime(2035, 2, 10, 12, 0)
        self.orchestrator = self.env["trend.scoring.orchestrator"]

        self.env["ir.config_parameter"].sudo().set_param(
            "winners.source_score_api", "0"
        )

        self.products = self.env["trend.product"].create([
            {
                "name": "Google Trends Test A",
                "product_ref": "GOOGLE-TRENDS-TEST-A",
                "source": "api",
                "country": "FR",
                "sales_count": 10,
            },
            {
                "name": "Google Trends Test B",
                "product_ref": "GOOGLE-TRENDS-TEST-B",
                "source": "api",
                "country": "FR",
                "sales_count": 10,
            },
        ])

    def test_daily_cron_stores_collected_interest(self):
        with patch.object(
            scoring_orchestrator,
            "fetch_search_volume",
            return_value=73,
        ) as collector:
            created = self.orchestrator.run_daily_scoring(
                computed_at=self.scoring_time
            )

        scores = created.filtered(
            lambda score: score.product_id in self.products
        )

        self.assertEqual(len(scores), 2)

        for product in self.products:
            score = scores.filtered(
                lambda record: record.product_id == product
            )
            self.assertEqual(score.search_volume, 73)

            collector.assert_any_call(
                product_name=product.name,
                country=product.country,
                computed_at=self.scoring_time,
            )

    def test_interest_does_not_change_score_or_ranking(self):
        with patch.object(
            scoring_orchestrator,
            "fetch_search_volume",
            side_effect=lambda **kwargs: (
                0 if kwargs["product_name"] == self.products[0].name
                else 100
            ),
        ):
            first = self.orchestrator.score_product(
                self.products[0],
                computed_at=self.scoring_time,
            )
            second = self.orchestrator.score_product(
                self.products[1],
                computed_at=self.scoring_time,
            )

        self.assertEqual(first.search_volume, 0)
        self.assertEqual(second.search_volume, 100)
        self.assertGreater(first.computed_score, 0)
        self.assertAlmostEqual(
            first.computed_score,
            second.computed_score,
            places=4,
        )

        ranked = self.orchestrator._recompute_daily_ranks(
            self.scoring_time
        )
        expected = ranked.sorted(
            key=lambda score: (-score.computed_score, score.id)
        )

        self.assertEqual(
            expected.mapped("rank"),
            list(range(1, len(expected) + 1)),
        )
        # Equal scores retain their ID order despite different interest.
        self.assertLess(first.rank, second.rank)

    def test_collector_uses_requested_day(self):
        keyword = "Test product"
        readings = pd.DataFrame(
            {keyword: [25, 73]},
            index=pd.to_datetime(["2035-02-09", "2035-02-10"]),
        )

        with patch("pytrends.request.TrendReq") as factory:
            client = factory.return_value
            client.interest_over_time.return_value = readings

            result = google_trends.fetch_search_volume(
                keyword, "fr", self.scoring_time
            )

        self.assertEqual(result, 73)
        client.build_payload.assert_called_once_with(
            [keyword],
            timeframe="2035-02-04 2035-02-10",
            geo="FR",
        )

    def test_collection_failure_does_not_stop_scoring(self):
        with patch(
            "pytrends.request.TrendReq",
            side_effect=TimeoutError("Simulated timeout"),
        ):
            with self.assertLogs(
                google_trends.__name__, level="ERROR"
            ):
                score = self.orchestrator.score_product(
                    self.products[0],
                    computed_at=self.scoring_time,
                )

        self.assertTrue(score.exists())
        self.assertEqual(score.search_volume, 0)
        self.assertGreater(score.computed_score, 0)