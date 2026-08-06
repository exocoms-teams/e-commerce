# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestTrendScore(TransactionCase):
    """Vérifie que trend.product.compute_trend_score() correspond exactement
    au calcul attendu (à la main / cf. score.md) pour un jeu de données connu.
    """

    def setUp(self):
        super().setUp()

        # Produit de test : sales_count=145, score_site_x=7.8
        # (reprend l'exemple "Montre connectée sport" du contrat d'ingestion)
        self.product = self.env['trend.product'].create({
            'name': 'Montre connectée sport (test)',
            'product_ref': 'TEST-SCORE-0001',
            'sales_count': 145,
            'score_site_x': 7.8,
            'country': 'MA',
            'source': 'api',
        })

        # Deux publicités liées, pour vérifier l'agrégation des likes/partages
        self.env['trend.ad'].create({
            'ad_ref': 'TEST-AD-001',
            'product_id': self.product.id,
            'country': 'MA',
            'social_network': 'facebook',
            'likes_count': 1230,
            'shares_count': 87,
        })
        self.env['trend.ad'].create({
            'ad_ref': 'TEST-AD-002',
            'product_id': self.product.id,
            'country': 'MA',
            'social_network': 'tiktok',
            'likes_count': 500,
            'shares_count': 20,
        })

    def test_compute_trend_score_matches_manual_calculation(self):
        # --- Calcul manuel de référence (voir score.md) ---
        # ventes=145, likes=1230+500=1730, partages=87+20=107, ads=2
        # Vol_T = 1.0*145 + 0.1*1730 + 0.3*107 + 0.5*2 = 351.1
        # Pas d'historique -> Vol_prev = 0 -> Growth_T = 351.1 / 1 = 351.1
        # source_score = 7.8/10 = 0.78
        # score = 351.1 * ln(352.1) * (1 + 0.2*0.78) = 2379.9967
        expected_score = 2379.9967

        score = self.product.compute_trend_score()

        self.assertEqual(len(self.product.ad_ids), 2)
        self.assertAlmostEqual(score, expected_score, places=4)