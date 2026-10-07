# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestTrendScore(TransactionCase):
    """Vérifie que trend.product.compute_trend_score() correspond exactement
    au calcul attendu (à la main / cf. score.md) pour un jeu de données connu.
    """

    def setUp(self):
        super().setUp()

        # Produit de test : sales_count/score_site_x conservés pour le contexte
        # métier, mais NE SONT PLUS lus par compute_trend_score() (Objectif 3 :
        # les métriques viennent désormais des snapshots trend.score, et
        # source_score vient de ir.config_parameter selon trend.product.source).
        self.product = self.env['trend.product'].create({
            'name': 'Montre connectée sport (test)',
            'product_ref': 'TEST-SCORE-0001',
            'sales_count': 145,
            'score_site_x': 7.8,
            'country': 'MA',
            'source': 'api',
        })

        # Snapshot unique, dans la fenêtre courante (0-30j) -> pas d'historique
        # antérieur -> Vol_T_prev = 0 (comme dans l'exemple manuel du score.md)
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_at': fields.Datetime.now(),
            'metric_sales': 145,          # ventes
            'metric_likes': 1730,         # 1230 + 500
            'metric_shares': 107,         # 87 + 20
            'metric_ads_count': 2,
            'computed_score': 0.0,        # non utilisé par le calcul, juste requis
        })

        # source_score = 0.78, équivalent au score_site_x/10 de l'ancien exemple,
        # mais récupéré ici via le mécanisme réel : ir.config_parameter par source.
        self.env['ir.config_parameter'].sudo().set_param(
            'winners.source_score_api', '0.78'
        )

    def test_compute_trend_score_matches_manual_calculation(self):
        # --- Calcul manuel de référence (voir score.md) ---
        # ventes=145, likes=1230+500=1730, partages=87+20=107, ads=2
        # Vol_T = 1.0*145 + 0.1*1730 + 0.3*107 + 0.5*2 = 351.1
        # Pas d'historique -> Vol_prev = 0 -> Growth_T = 351.1 / 1 = 351.1
        # source_score = 0.78 (ir.config_parameter, source='api')
        # score = 351.1 * ln(352.1) * (1 + 0.2*0.78) = 2379.9967
        expected_score = 2379.9967

        score = self.product.compute_trend_score()

        self.assertEqual(len(self.product.ad_ids), 0)  # plus lu par le calcul
        self.assertAlmostEqual(score, expected_score, places=4)

    @mute_logger('odoo.sql_db')
    def test_only_one_score_per_product_and_day_is_allowed(self):
        """La contrainte SQL bloque aussi deux heures distinctes du même jour."""
        product = self.env['trend.product'].create({
            'name': 'Produit contrainte score quotidien',
            'product_ref': 'TEST-SCORE-DAILY-UNIQUE',
            'country': 'MA',
            'source': 'api',
        })
        score_model = self.env['trend.score']
        score_model.create({
            'product_id': product.id,
            'computed_at': '2026-08-27 09:00:00',
        })

        with self.cr.savepoint():
            with self.assertRaises(Exception):
                score_model.create({
                    'product_id': product.id,
                    'computed_at': '2026-08-27 18:00:00',
                })

        next_day_score = score_model.create({
            'product_id': product.id,
            'computed_at': '2026-08-28 09:00:00',
        })
        self.assertTrue(next_day_score.id)


class TestTrendScoreScenarios(TransactionCase):
    """Exercise real snapshots, metric changes and daily ranking."""

    def setUp(self):
        super().setUp()
        self.orchestrator = self.env['trend.scoring.orchestrator']
        self.env['ir.config_parameter'].sudo().set_param(
            'winners.source_score_api', '0.0'
        )
        self.first_day = '2035-01-10 09:00:00'
        self.second_day = '2035-01-11 09:00:00'
        self.product = self._create_product('BASE', sales=10)

    def _create_product(self, suffix, sales):
        return self.env['trend.product'].create({
            'name': 'Score scenario ' + suffix,
            'product_ref': 'TEST-SCORE-SCENARIO-' + suffix,
            'sales_count': sales,
            'country': 'FR',
            'source': 'api',
        })

    def _create_ad(self):
        return self.env['trend.ad'].create({
            'ad_ref': 'TEST-SCORE-SCENARIO-AD',
            'product_id': self.product.id,
            'country': 'FR',
            'social_network': 'tiktok',
            'likes_count': 100,
            'shares_count': 10,
            'is_active': True,
            'collected_at': self.first_day,
        })

    def _first_snapshot(self):
        return self.orchestrator.score_product(
            self.product, computed_at=self.first_day
        )

    def _second_snapshot(self):
        return self.orchestrator.score_product(
            self.product, computed_at=self.second_day
        )

    def test_real_positive_growth_matches_manual_calculation(self):
        import math

        ad = self._create_ad()
        first_score = self._first_snapshot()
        self.assertEqual(first_score.metric_sales, 10)
        self.assertEqual(first_score.metric_likes, 100)
        self.assertEqual(first_score.metric_shares, 10)
        self.assertEqual(first_score.metric_ads_count, 1)
        first_value = first_score.computed_score

        self.product.write({'sales_count': 20})
        ad.write({'likes_count': 200, 'shares_count': 20})
        second_score = self._second_snapshot()

        # Explicit volumes from the documented weights, not the engine itself.
        previous_volume = 10 + 0.1 * 100 + 0.3 * 10 + 0.5 * 1
        current_volume = 20 + 0.1 * 200 + 0.3 * 20 + 0.5 * 1
        growth = (current_volume - previous_volume) / (previous_volume + 1.0)
        expected = round(growth * math.log(1 + current_volume), 4)

        self.assertGreater(growth, 0.0)
        self.assertGreater(second_score.computed_score, 0.0)
        self.assertAlmostEqual(second_score.computed_score, expected, places=4)
        self.assertEqual(second_score.metric_sales, 20)
        self.assertEqual(second_score.metric_likes, 200)
        self.assertEqual(second_score.metric_shares, 20)
        self.assertEqual(second_score.metric_ads_count, 1)
        self.assertNotEqual(first_score.score_date, second_score.score_date)
        self.assertEqual(len(self.product.score_ids), 2)
        self.assertAlmostEqual(self.product.current_score, expected, places=4)
        # The previous snapshot must remain unchanged after live metrics change.
        self.assertEqual(first_score.metric_sales, 10)
        self.assertEqual(first_score.metric_likes, 100)
        self.assertEqual(first_score.metric_shares, 10)
        self.assertAlmostEqual(first_score.computed_score, first_value, places=4)

    def test_equal_metrics_return_exactly_zero(self):
        self._create_ad()
        first_score = self._first_snapshot()
        self.assertGreater(first_score.computed_score, 0.0)

        second_score = self._second_snapshot()

        self.assertEqual(second_score.metric_sales, first_score.metric_sales)
        self.assertEqual(second_score.metric_likes, first_score.metric_likes)
        self.assertEqual(second_score.metric_shares, first_score.metric_shares)
        self.assertEqual(second_score.metric_ads_count, first_score.metric_ads_count)
        self.assertEqual(second_score.computed_score, 0.0)
        self.assertEqual(self.product.current_score, 0.0)

    def test_lower_metrics_return_exactly_zero(self):
        ad = self._create_ad()
        first_score = self._first_snapshot()
        self.assertGreater(first_score.computed_score, 0.0)

        self.product.write({'sales_count': 5})
        ad.write({'likes_count': 50, 'shares_count': 5})
        second_score = self._second_snapshot()

        previous_volume = 10 + 0.1 * 100 + 0.3 * 10 + 0.5
        current_volume = 5 + 0.1 * 50 + 0.3 * 5 + 0.5
        growth = (current_volume - previous_volume) / (previous_volume + 1.0)
        self.assertLess(growth, 0.0)
        self.assertEqual(second_score.metric_sales, 5)
        self.assertEqual(second_score.metric_likes, 50)
        self.assertEqual(second_score.metric_shares, 5)
        self.assertEqual(second_score.computed_score, 0.0)
        self.assertEqual(self.product.current_score, 0.0)

    def test_product_without_ads_builds_metrics_and_scores_normally(self):
        import math

        self.assertFalse(self.product.ad_ids)
        self.assertEqual(self.product.build_current_metrics(), {
            'ventes': 10,
            'likes': 0,
            'partages': 0,
            'ads': 0,
        })
        first_score = self._first_snapshot()
        self.assertAlmostEqual(
            first_score.computed_score, round(10 * math.log(11), 4), places=4
        )
        self.assertEqual(first_score.metric_likes, 0)
        self.assertEqual(first_score.metric_shares, 0)
        self.assertEqual(first_score.metric_ads_count, 0)

        self.product.write({'sales_count': 20})
        second_score = self._second_snapshot()
        expected = round(((20 - 10) / (10 + 1.0)) * math.log(21), 4)
        self.assertFalse(self.product.ad_ids)
        self.assertAlmostEqual(second_score.computed_score, expected, places=4)
        self.assertEqual(second_score.metric_likes, 0)
        self.assertEqual(second_score.metric_shares, 0)
        self.assertEqual(second_score.metric_ads_count, 0)

    def test_daily_cron_ranks_scores_in_descending_order(self):
        import math

        medium = self._create_product('RANK-MEDIUM', sales=20)
        best = self._create_product('RANK-BEST', sales=30)
        products = self.product | medium | best
        scoring_time = '2035-01-12 09:00:00'

        created = self.orchestrator.run_daily_scoring(computed_at=scoring_time)
        our_scores = created.filtered(lambda score: score.product_id in products)
        self.assertEqual(len(our_scores), 3)
        self.assertEqual(
            our_scores.sorted('rank').mapped('product_id').ids,
            [best.id, medium.id, self.product.id],
        )
        for product, sales in ((self.product, 10), (medium, 20), (best, 30)):
            score = our_scores.filtered(lambda item: item.product_id == product)
            self.assertAlmostEqual(
                score.computed_score,
                round(sales * math.log(1 + sales), 4),
                places=4,
            )

        # Other products may exist: validate the complete day's ranking too.
        daily_scores = self.env['trend.score'].search([
            ('score_date', '=', '2035-01-12'),
        ], order='rank asc, id asc')
        self.assertEqual(daily_scores.mapped('rank'), list(range(1, len(daily_scores) + 1)))
        self.assertEqual(
            daily_scores.ids,
            daily_scores.sorted(lambda score: (-score.computed_score, score.id)).ids,
        )

        # Running the same day again must retain the existing snapshots/ranks.
        original_ids = daily_scores.ids
        original_ranks = daily_scores.mapped('rank')
        repeated = self.orchestrator.run_daily_scoring(computed_at=scoring_time)
        self.assertFalse(repeated)
        after = self.env['trend.score'].search([
            ('score_date', '=', '2035-01-12'),
        ], order='rank asc, id asc')
        self.assertEqual(after.ids, original_ids)
        self.assertEqual(after.mapped('rank'), original_ranks)
