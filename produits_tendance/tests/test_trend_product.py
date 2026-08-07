from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestTrendProductConstraints(TransactionCase):
    """Epic 1.A - Modèle Produits : contraintes et validations de
    trend.product (sales_count non négatif, product_ref unique)."""

    def test_sales_count_negative_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            self.env['trend.product'].create({
                'name': 'Produit test',
                'product_ref': 'TEST-CONSTRAINT-0001',
                'sales_count': -5,
                'source': 'api',
            })

    def test_sales_count_zero_or_positive_is_valid(self):
        product = self.env['trend.product'].create({
            'name': 'Produit test',
            'product_ref': 'TEST-CONSTRAINT-0002',
            'sales_count': 0,
            'source': 'api',
        })
        self.assertEqual(product.sales_count, 0)

    @mute_logger('odoo.sql_db')
    def test_duplicate_product_ref_raises_integrity_error(self):
        self.env['trend.product'].create({
            'name': 'Produit test A',
            'product_ref': 'TEST-CONSTRAINT-DUP',
            'source': 'api',
        })
        with self.assertRaises(Exception):
            self.env['trend.product'].create({
                'name': 'Produit test B',
                'product_ref': 'TEST-CONSTRAINT-DUP',
                'source': 'api',
            })


class TestTrendProductComputeScore(TransactionCase):
    """current_score reflète toujours le dernier trend.score (par
    computed_at), pas le premier ni une moyenne."""

    def setUp(self):
        super().setUp()
        self.product = self.env['trend.product'].create({
            'name': 'Produit test score',
            'product_ref': 'TEST-CURRENTSCORE-0001',
            'source': 'api',
        })

    def test_current_score_zero_without_any_score(self):
        self.assertEqual(self.product.current_score, 0.0)

    def test_current_score_reflects_latest_score(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 10.0,
            'computed_at': '2026-07-01 09:00:00',
        })
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 25.0,
            'computed_at': '2026-07-05 09:00:00',
        })
        self.assertEqual(self.product.current_score, 25.0)


class TestTrendProductRanking(TransactionCase):
    """rank_number / is_top_10 / is_top_3 (compute + méthodes de recherche
    _search_is_top_10 / _search_is_top_3), utilisés par la vue Admin de
    classement (Epic 1.B, "Créer la vue Admin de classement des produits
    gagnants")."""

    def setUp(self):
        super().setUp()
        # Scores très élevés (5000+) pour dominer tout produit de démo déjà
        # en base (demo/dashboard_demo.xml monte jusqu'à 92.5) et garder un
        # classement prévisible.
        self.products = []
        for i in range(5):
            product = self.env['trend.product'].create({
                'name': f'Produit classement {i}',
                'product_ref': f'TEST-RANK-{i}',
                'source': 'api',
            })
            self.env['trend.score'].create({
                'product_id': product.id,
                'computed_score': 5000.0 - i,
            })
            self.products.append(product)

    def test_rank_number_follows_score_descending(self):
        # products[0] a le score le plus élevé (5000.0) -> rang 1
        self.assertEqual(self.products[0].rank_number, 1)
        self.assertEqual(self.products[1].rank_number, 2)
        self.assertEqual(self.products[4].rank_number, 5)

    def test_is_top_3_matches_rank(self):
        self.assertTrue(self.products[0].is_top_3)
        self.assertTrue(self.products[2].is_top_3)
        self.assertFalse(self.products[3].is_top_3)

    def test_is_top_10_true_when_fewer_than_10_products_total(self):
        """Avec moins de 10 produits en base au total (au-delà des données
        de démo, tant qu'elles ne dépassent pas 92.5 < 5000), tous les
        produits de ce test doivent être considérés top 10."""
        self.assertTrue(self.products[4].is_top_10)

    def test_search_is_top_3_domain_returns_only_top_3(self):
        found = self.env['trend.product'].search([
            ('id', 'in', [p.id for p in self.products]),
            ('is_top_3', '=', True),
        ])
        self.assertEqual(len(found), 3)
        self.assertEqual(set(found.ids), {self.products[0].id, self.products[1].id, self.products[2].id})

    def test_search_is_top_3_false_excludes_top_3(self):
        found = self.env['trend.product'].search([
            ('id', 'in', [p.id for p in self.products]),
            ('is_top_3', '=', False),
        ])
        self.assertEqual(set(found.ids), {self.products[3].id, self.products[4].id})
