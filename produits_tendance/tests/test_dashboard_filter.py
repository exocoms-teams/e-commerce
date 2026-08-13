from odoo.tests.common import HttpCase
from ..controllers.dashboard_api import TrendDashboardAPI


class TestDashboardFilterAPI(HttpCase):
    """Vérifie TrendDashboardAPI.get_product_list() / get_filter_options()
    et la route /api/dashboard/filter (WIN-45 / WIN-50)."""

    def setUp(self):
        super().setUp()
        self.cat_electronique = self.env['trend.category'].create({'name': 'Électronique'})
        self.cat_maison = self.env['trend.category'].create({'name': 'Maison'})

        self.product_ma = self.env['trend.product'].create({
            'name': 'Lampe LED (test)',
            'product_ref': 'TEST-FILTER-0001',
            'category_id': self.cat_maison.id,
            'country': 'MA',
            'source': 'api',
        })
        self.env['trend.score'].create({
            'product_id': self.product_ma.id,
            'computed_score': 30.0,
        })

        self.product_fr = self.env['trend.product'].create({
            'name': 'Écouteurs sans fil (test)',
            'product_ref': 'TEST-FILTER-0002',
            'category_id': self.cat_electronique.id,
            'country': 'FR',
            'source': 'api',
        })
        self.env['trend.score'].create({
            'product_id': self.product_fr.id,
            'computed_score': 80.0,
        })

    def test_get_product_list_without_filter_returns_all_sorted_by_score(self):
        api = TrendDashboardAPI(self.env)
        data = api.get_product_list()
        ids = [p['id'] for p in data]
        self.assertIn(self.product_ma.id, ids)
        self.assertIn(self.product_fr.id, ids)
        # Score décroissant : le produit FR (80.0) doit précéder le MA (30.0)
        self.assertLess(ids.index(self.product_fr.id), ids.index(self.product_ma.id))

    def test_get_product_list_filters_by_category(self):
        api = TrendDashboardAPI(self.env)
        data = api.get_product_list(category_id=self.cat_maison.id)
        ids = [p['id'] for p in data]
        self.assertIn(self.product_ma.id, ids)
        self.assertNotIn(self.product_fr.id, ids)

    def test_get_product_list_filters_by_country(self):
        api = TrendDashboardAPI(self.env)
        data = api.get_product_list(country='FR')
        ids = [p['id'] for p in data]
        self.assertIn(self.product_fr.id, ids)
        self.assertNotIn(self.product_ma.id, ids)

    def test_get_product_list_combines_filters(self):
        api = TrendDashboardAPI(self.env)
        data = api.get_product_list(category_id=self.cat_maison.id, country='FR')
        self.assertEqual(data, [])

    def test_get_filter_options_lists_categories_and_countries(self):
        api = TrendDashboardAPI(self.env)
        options = api.get_filter_options()
        category_names = [c['name'] for c in options['categories']]
        self.assertIn('Électronique', category_names)
        self.assertIn('Maison', category_names)
        self.assertIn('MA', options['countries'])
        self.assertIn('FR', options['countries'])

    def test_api_dashboard_filter_route_returns_json(self):
        response = self.url_open(
            '/api/dashboard/filter?country=FR'
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['status'], 'success')
        ids = [p['id'] for p in payload['products']]
        self.assertIn(self.product_fr.id, ids)
        self.assertNotIn(self.product_ma.id, ids)