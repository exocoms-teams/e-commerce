from odoo.tests.common import TransactionCase
from ..controllers.dashboard_api import TrendDashboardAPI


class TestScoreHistory(TransactionCase):
    """Vérifie TrendDashboardAPI.get_score_history() : un point par jour,
    trié chronologiquement."""

    def setUp(self):
        super().setUp()
        self.product = self.env['trend.product'].create({
            'name': 'Produit historique (test)',
            'product_ref': 'TEST-HISTORY-0001',
            'country': 'MA',
            'source': 'api',
        })

    def test_get_score_history_empty_without_scores(self):
        api = TrendDashboardAPI(self.env)
        self.assertEqual(api.get_score_history(self.product), [])

    def test_get_score_history_sorted_chronologically(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 10.0,
            'computed_at': '2026-07-10 09:00:00',
        })
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 20.0,
            'computed_at': '2026-07-08 09:00:00',
        })
        api = TrendDashboardAPI(self.env)
        history = api.get_score_history(self.product)

        self.assertEqual([point['date'] for point in history], ['2026-07-08', '2026-07-10'])
        self.assertEqual([point['score'] for point in history], [20.0, 10.0])

