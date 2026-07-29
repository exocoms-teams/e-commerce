from odoo.tests.common import TransactionCase
from ..controllers.dashboard_api import TrendDashboardAPI


class TestDashboardAPI(TransactionCase):
    """Vérifie TrendDashboardAPI.get_dashboard_products() : tri par score
    décroissant, et surtout la limite Freemium (WIN-48) — doit être
    appliquée dans la requête ORM elle-même."""

    def setUp(self):
        super().setUp()
        self.products = self.env['trend.product']
        for i in range(7):
            product = self.env['trend.product'].create({
                'name': f'Produit test {i}',
                'product_ref': f'TEST-DASHBOARD-{i}',
                'country': 'MA',
                'source': 'api',
            })
            self.env['trend.score'].create({
                'product_id': product.id,
                'computed_score': float(i),
            })
            self.products |= product

    def test_get_dashboard_products_without_limit_returns_all(self):
        api = TrendDashboardAPI(self.env)
        result = api.get_dashboard_products()
        self.assertEqual(len(result), 7)

    def test_get_dashboard_products_orders_by_current_score_desc(self):
        api = TrendDashboardAPI(self.env)
        result = api.get_dashboard_products()
        scores = result.mapped('current_score')
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_get_dashboard_products_applies_freemium_limit(self):
        api = TrendDashboardAPI(self.env)
        result = api.get_dashboard_products(limit=5)
        self.assertEqual(len(result), 5)
        # Les 5 produits retournés doivent être les mieux scorés (6, 5, 4, 3, 2).
        self.assertEqual(result.mapped('current_score'), [6.0, 5.0, 4.0, 3.0, 2.0])
