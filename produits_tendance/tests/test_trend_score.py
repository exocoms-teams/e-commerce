# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests.common import TransactionCase


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