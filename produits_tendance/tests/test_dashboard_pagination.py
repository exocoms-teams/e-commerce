from odoo.tests.common import TransactionCase
from ..controllers.dashboard_api import TrendDashboardAPI


class TestPaginationLimit(TransactionCase):
    """WIN-77 : get_pagination_limit ne doit jamais laisser un compte
    Gratuit dépasser 5 résultats, même via offset/limit manipulés."""

    def setUp(self):
        super().setUp()
        self.free_user = self.env['res.users'].create({
            'name': 'Free Pagination Test',
            'login': 'free_pagination_test@example.com',
            'group_ids': [(6, 0, [self.env.ref('produits_tendance.group_trend_free').id])],
        })
        self.standard_user = self.env['res.users'].create({
            'name': 'Standard Pagination Test',
            'login': 'standard_pagination_test@example.com',
            'group_ids': [(6, 0, [self.env.ref('produits_tendance.group_trend_standard').id])],
        })

    def test_free_user_default_limit_is_5(self):
        limit, offset = TrendDashboardAPI.get_pagination_limit(self.env(user=self.free_user))
        self.assertEqual((limit, offset), (5, 0))

    def test_free_user_offset_beyond_5_returns_nothing(self):
        limit, offset = TrendDashboardAPI.get_pagination_limit(
            self.env(user=self.free_user), requested_offset=5)
        self.assertEqual((limit, offset), (0, 0))

    def test_free_user_cannot_inflate_limit_via_url(self):
        """Simule ?offset=0 avec un limit manipulé à 999 : le plafond reste 5."""
        limit, offset = TrendDashboardAPI.get_pagination_limit(
            self.env(user=self.free_user), requested_offset=0, requested_limit=999)
        self.assertEqual((limit, offset), (5, 0))

    def test_free_user_partial_offset_clamped(self):
        """offset=3 -> il ne reste que 5-3=2 produits accessibles."""
        limit, offset = TrendDashboardAPI.get_pagination_limit(
            self.env(user=self.free_user), requested_offset=3)
        self.assertEqual((limit, offset), (2, 3))

    def test_standard_user_default_limit_is_20(self):
        limit, offset = TrendDashboardAPI.get_pagination_limit(self.env(user=self.standard_user))
        self.assertEqual((limit, offset), (20, 0))

    def test_standard_user_offset_paginates_normally(self):
        limit, offset = TrendDashboardAPI.get_pagination_limit(
            self.env(user=self.standard_user), requested_offset=20)
        self.assertEqual((limit, offset), (20, 20))


class TestPaginationNoDuplicates(TransactionCase):
    """Vérifie qu'aucun produit n'apparaît deux fois entre deux pages."""

    def setUp(self):
        super().setUp()
        self.products = self.env['trend.product']
        for i in range(7):
            p = self.env['trend.product'].create({
                'name': f'Pagination Produit {i}',
                'product_ref': f'TEST-PAGINATION-{i}',
                'country': 'MA',
                'source': 'api',
            })
            self.env['trend.score'].create({'product_id': p.id, 'computed_score': 5000.0 + i})
            self.products |= p

    def test_two_pages_do_not_overlap(self):
        api = TrendDashboardAPI(self.env)
        page1 = api.get_product_list(limit=3, offset=0)
        page2 = api.get_product_list(limit=3, offset=3)
        ids1 = {p['id'] for p in page1}
        ids2 = {p['id'] for p in page2}
        self.assertEqual(len(ids1), 3)
        self.assertEqual(len(ids2), 3)
        self.assertFalse(ids1 & ids2, "Pas de doublon entre page 1 et page 2")