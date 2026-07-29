from odoo.tests.common import TransactionCase
from ..controllers.dashboard_api import TrendDashboardAPI


class TestScoreHistory(TransactionCase):
    """Vérifie TrendDashboardAPI.get_score_history() : agrégation par date
    (WIN-52) — un point par jour, moyenne si plusieurs calculs le même jour,
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

    def test_get_score_history_averages_same_day_scores(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 10.0,
            'computed_at': '2026-07-10 09:00:00',
        })
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 20.0,
            'computed_at': '2026-07-10 18:00:00',
        })
        api = TrendDashboardAPI(self.env)
        history = api.get_score_history(self.product)

        self.assertEqual(history, [{'date': '2026-07-10', 'score': 15.0}])

    def test_get_score_history_ignores_scores_without_computed_at(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 5.0,
        })
        api = TrendDashboardAPI(self.env)
        self.assertEqual(api.get_score_history(self.product), [])
