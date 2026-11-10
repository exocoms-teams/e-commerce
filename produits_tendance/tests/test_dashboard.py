from odoo.tests.common import TransactionCase
from ..controllers.dashboard_api import TrendDashboardAPI


class TestDashboardAPI(TransactionCase):
    """Vérifie TrendDashboardAPI.get_dashboard_products() : tri par score
    décroissant, et surtout la limite Freemium (WIN-48) — doit être
    appliquée dans la requête ORM elle-même."""

    def setUp(self):
        super().setUp()
        # Scores tres eleves (1000+) pour garantir que ces produits de test
        # dominent toujours le classement, quelles que soient les donnees de
        # demo presentes en base (demo/dashboard_demo.xml, WIN-45/50, monte
        # jusqu'a 92.5) - sinon get_dashboard_products() (recherche globale,
        # sans domaine) melange les deux et rend les assertions imprevisibles.
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
                'computed_score': 1000.0 + i,
            })
            self.products |= product

    def test_get_dashboard_products_without_limit_returns_all(self):
        api = TrendDashboardAPI(self.env)
        result = api.get_dashboard_products()
        # Intersection avec self.products : get_dashboard_products() renvoie
        # TOUS les trend.product (y compris les donnees de demo), donc on ne
        # peut pas supposer que la base ne contient que les 7 crees ici.
        self.assertEqual(len(result & self.products), 7)

    def test_get_dashboard_products_orders_by_current_score_desc(self):
        api = TrendDashboardAPI(self.env)
        result = api.get_dashboard_products()
        scores = result.mapped('current_score')
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_get_dashboard_products_applies_freemium_limit(self):
        api = TrendDashboardAPI(self.env)
        result = api.get_dashboard_products(limit=5)
        self.assertEqual(len(result), 5)
        # Les 5 produits retournés doivent être les mieux scorés (1006 à 1002).
        self.assertEqual(result.mapped('current_score'), [1006.0, 1005.0, 1004.0, 1003.0, 1002.0])

    def test_get_dashboard_products_works_without_sudo_for_freemium_user(self):
        """group_trend_free implique group_trend_user (lecture) : un compte
        Freemium doit pouvoir lire trend.product sans AccessError, avec ses
        propres droits (pas de sudo dans get_dashboard_products)."""
        free_user = self.env['res.users'].create({
            'name': 'Freemium Test User',
            'login': 'freemium_test_user@example.com',
            'group_ids': [(6, 0, [self.env.ref('produits_tendance.group_trend_free').id])],
        })
        api = TrendDashboardAPI(self.env(user=free_user))
        result = api.get_dashboard_products(limit=5)
        self.assertEqual(len(result), 5)

    def test_get_dashboard_stats_counts_all_products(self):
        """get_dashboard_stats() ne connaît pas les 7 produits créés dans
        setUp() comme un ensemble à part : il compte TOUT trend.product en
        base (y compris les données de demo). On vérifie donc un delta
        avant/après création plutôt qu'un total absolu, pour rester robuste
        indépendamment des données de démo déjà présentes."""
        api = TrendDashboardAPI(self.env)
        before = api.get_dashboard_stats()

        extra = self.env['trend.product'].create({
            'name': 'Produit stats supplémentaire',
            'product_ref': 'TEST-DASHBOARD-STATS-EXTRA',
            'country': 'MA',
            'source': 'api',
        })
        self.env['trend.score'].create({
            'product_id': extra.id,
            'computed_score': 2000.0,
        })

        after = api.get_dashboard_stats()
        self.assertEqual(after['total_products'], before['total_products'] + 1)
        self.assertGreater(after['avg_score'], before['avg_score'])

    def test_get_dashboard_stats_avg_score_zero_without_products(self):
        """Cas limite : aucun trend.product en base -> score moyen à 0.0,
        pas de ZeroDivisionError."""
        self.env['trend.product'].search([]).unlink()
        api = TrendDashboardAPI(self.env)
        stats = api.get_dashboard_stats()
        self.assertEqual(stats, {'total_products': 0, 'avg_score': 0.0})
