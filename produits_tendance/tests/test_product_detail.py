from werkzeug.exceptions import NotFound
from odoo.tests.common import HttpCase
from ..controllers.dashboard_api import TrendDashboardAPI


class TestProductDetailAPI(HttpCase):
    """Vérifie TrendDashboardAPI.get_product_detail() : cas nominal et 404."""

    def setUp(self):
        super().setUp()
        self.product = self.env['trend.product'].create({
            'name': 'Écouteurs sans fil (test)',
            'product_ref': 'TEST-DETAIL-0001',
            'sales_count': 50,
            'country': 'MA',
            'source': 'api',
        })
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 42.5,
            'search_volume': 1200,
        })

    def test_get_product_detail_returns_expected_data(self):
        api = TrendDashboardAPI(self.env)
        data = api.get_product_detail(self.product.id)

        self.assertEqual(data['product'], self.product)
        self.assertEqual(data['trend_score'], 42.5)
        self.assertEqual(data['search_volume'], 1200)

    def test_get_product_detail_raises_404_for_unknown_id(self):
        api = TrendDashboardAPI(self.env)
        with self.assertRaises(NotFound):
            api.get_product_detail(999999)

    def test_get_product_detail_without_score_falls_back_to_current_score(self):
        product_no_score = self.env['trend.product'].create({
            'name': 'Produit sans score (test)',
            'product_ref': 'TEST-DETAIL-0002',
            'country': 'MA',
            'source': 'api',
        })
        api = TrendDashboardAPI(self.env)
        data = api.get_product_detail(product_no_score.id)

        self.assertIsNone(data['search_volume'])
        self.assertEqual(data['trend_score'], product_no_score.current_score)