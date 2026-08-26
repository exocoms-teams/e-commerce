from odoo import fields
from odoo.tests.common import TransactionCase

from ..services.scoring_engine import ScoringEngine


class TestTrendScoringOrchestrator(TransactionCase):

    def setUp(self):
        super().setUp()

        self.product = self.env['trend.product'].create({
            'name': 'Produit test orchestration',
            'product_ref': 'ORCHESTRATOR-TEST-001',
            'source': 'api',
            'sales_count': 10,
        })

        self.ad = self.env['trend.ad'].create({
            'ad_ref': 'AD-ORCHESTRATOR-001',
            'product_id': self.product.id,
            'country': 'MA',
            'social_network': 'facebook',
            'likes_count': 10,
            'shares_count': 2,
            'is_active': True,
        })

        self.orchestrator = self.env[
            'trend.scoring.orchestrator'
        ]

    def test_two_daily_calls_create_two_score_snapshots(self):
        first_day = '2026-08-22 09:00:00'
        second_day = '2026-08-23 09:00:00'

        first_score = self.orchestrator.score_product(
            self.product,
            computed_at=first_day,
        )

        self.assertTrue(first_score)
        self.assertEqual(
            first_score.metric_sales,
            10,
        )
        self.assertEqual(
            first_score.metric_likes,
            10,
        )
        self.assertEqual(
            first_score.metric_shares,
            2,
        )
        self.assertEqual(
            first_score.metric_ads_count,
            1,
        )

        # Modification des métriques avant le deuxième calcul.
        self.product.write({
            'sales_count': 20,
        })

        self.ad.write({
            'likes_count': 20,
            'shares_count': 4,
        })

        second_score = self.orchestrator.score_product(
            self.product,
            computed_at=second_day,
        )

        product_scores = self.env['trend.score'].search([
            ('product_id', '=', self.product.id),
        ])

        self.assertEqual(len(product_scores), 2)

        self.assertNotEqual(
            first_score.id,
            second_score.id,
        )

        self.assertEqual(
            second_score.metric_sales,
            20,
        )
        self.assertEqual(
            second_score.metric_likes,
            20,
        )
        self.assertEqual(
            second_score.metric_shares,
            4,
        )
        self.assertEqual(
            second_score.metric_ads_count,
            1,
        )

        # Reproduction du calcul attendu du deuxième jour.
        previous_metrics = {
            'ventes': first_score.metric_sales,
            'likes': first_score.metric_likes,
            'partages': first_score.metric_shares,
            'ads': first_score.metric_ads_count,
        }

        current_metrics = {
            'ventes': second_score.metric_sales,
            'likes': second_score.metric_likes,
            'partages': second_score.metric_shares,
            'ads': second_score.metric_ads_count,
        }

        expected_second_score = ScoringEngine().calculate_trend_score(
            current_metrics=current_metrics,
            previous_metrics=previous_metrics,
            source_score=0.0,
        )

        self.assertAlmostEqual(
            second_score.computed_score,
            expected_second_score,
            places=4,
        )

        # Le premier snapshot ne doit jamais avoir été modifié.
        self.assertEqual(first_score.metric_sales, 10)
        self.assertEqual(first_score.metric_likes, 10)
        self.assertEqual(first_score.metric_shares, 2)