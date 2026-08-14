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
            'price': 50.0,
        })
        self.env['trend.score'].create({
            'product_id': self.product_ma.id,
            'computed_score': 998.0,
        })

        self.product_fr = self.env['trend.product'].create({
            'name': 'Écouteurs sans fil (test)',
            'product_ref': 'TEST-FILTER-0002',
            'category_id': self.cat_electronique.id,
            'country': 'FR',
            'source': 'scraping',
            'price': 300.0,
        })
        # Score tres eleve pour garantir que ce produit reste le mieux
        # score globalement (test_get_product_list_applies_limit), quelles
        # que soient les donnees de demo presentes (demo/dashboard_demo.xml,
        # WIN-45/50, monte jusqu'a 92.5).
        self.env['trend.score'].create({
            'product_id': self.product_fr.id,
            'computed_score': 999.0,
        })
        

    def test_get_product_list_without_filter_returns_all_sorted_by_score(self):
        api = TrendDashboardAPI(self.env)
        data = api.get_product_list()
        ids = [p['id'] for p in data]
        self.assertIn(self.product_ma.id, ids)
        self.assertIn(self.product_fr.id, ids)
        # Score décroissant : le produit FR (999.0) doit précéder le MA (30.0)
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

    def test_get_product_list_applies_limit(self):
        """La limite Freemium (WIN-48) doit etre appliquee cote ORM, meme
        principe que get_dashboard_products - regression du merge des
        filtres dynamiques (WIN-45/50) qui l'avait perdue sur /dashboard
        et /api/dashboard/filter."""
        api = TrendDashboardAPI(self.env)
        data = api.get_product_list(limit=1)
        self.assertEqual(len(data), 1)
        # Le mieux score (FR, 999.0) doit etre celui retourne.
        self.assertEqual(data[0]['id'], self.product_fr.id)
    def test_get_product_list_filters_by_price_max(self):
       api = TrendDashboardAPI(self.env)
       data = api.get_product_list(price_max=200)
       ids = [p['id'] for p in data]
       self.assertIn(self.product_ma.id, ids)
       self.assertNotIn(self.product_fr.id, ids)

    def test_get_product_list_filters_by_source(self):
       api = TrendDashboardAPI(self.env)
       data = api.get_product_list(source='api')
       ids = [p['id'] for p in data]
       self.assertIn(self.product_ma.id, ids)
       self.assertNotIn(self.product_fr.id, ids)

   def test_get_product_list_combines_price_and_source(self):
       api = TrendDashboardAPI(self.env)
       data = api.get_product_list(price_max=200, source='api')
       ids = [p['id'] for p in data]
       self.assertIn(self.product_ma.id, ids)
       self.assertNotIn(self.product_fr.id, ids)
       self.assertEqual(ids[0], self.product_ma.id)

    def test_api_dashboard_filter_route_price_and_source(self):
       response = self.url_open('/api/dashboard/filter?price_max=200&source=api')
       self.assertEqual(response.status_code, 200)
       payload = response.json()
       ids = [p['id'] for p in payload['products']]
       self.assertIn(self.product_ma.id, ids)
       self.assertNotIn(self.product_fr.id, ids)

    def test_dashboard_page_respects_price_and_source_in_url(self):
       response = self.url_open('/dashboard?price_max=200&source=api')
       self.assertEqual(response.status_code, 200)
       # le produit FR (300, scraping) ne doit pas apparaître dans le HTML rendu
       self.assertNotIn(b'Ecouteurs sans fil', response.content)