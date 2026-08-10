from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestTrendAdAutoLinking(TransactionCase):
    """Epic 1.C - Modèle Publicités : create() doit rattacher
    automatiquement trend.ad à un trend.product existant (par product_ref),
    ou en créer un nouveau si nécessaire (voir models/trend_ad.py)."""

    def test_create_links_to_existing_product_by_ref(self):
        product = self.env['trend.product'].create({
            'name': 'Produit existant',
            'product_ref': 'TEST-AD-LINK-0001',
            'source': 'api',
        })
        ad = self.env['trend.ad'].create({
            'ad_ref': 'AD-REF-0001',
            'product_ref': 'TEST-AD-LINK-0001',
            'country': 'MA',
            'social_network': 'facebook',
        })
        self.assertEqual(ad.product_id, product)
        # Aucun nouveau trend.product ne doit avoir été créé.
        self.assertEqual(
            self.env['trend.product'].search_count([('product_ref', '=', 'TEST-AD-LINK-0001')]),
            1,
        )

    def test_create_auto_creates_product_when_missing(self):
        ad = self.env['trend.ad'].create({
            'ad_ref': 'AD-REF-0002',
            'product_ref': 'TEST-AD-LINK-0002',
            'product_name': 'Nouveau produit auto-créé',
            'country': 'FR',
            'social_network': 'tiktok',
        })
        self.assertTrue(ad.product_id)
        self.assertEqual(ad.product_id.product_ref, 'TEST-AD-LINK-0002')
        self.assertEqual(ad.product_id.name, 'Nouveau produit auto-créé')
        self.assertEqual(ad.product_id.source, 'api')

    def test_create_auto_created_product_falls_back_to_generic_name(self):
        """Sans product_name fourni, le produit auto-créé reçoit un nom de
        secours explicite plutôt qu'un nom vide."""
        ad = self.env['trend.ad'].create({
            'ad_ref': 'AD-REF-0003',
            'product_ref': 'TEST-AD-LINK-0003',
            'country': 'MA',
            'social_network': 'instagram',
        })
        self.assertIn('TEST-AD-LINK-0003', ad.product_id.name)

    def test_create_with_explicit_product_id_does_not_use_product_ref_logic(self):
        """Si product_id est déjà fourni explicitement, product_ref ne doit
        pas déclencher de recherche/création supplémentaire."""
        product = self.env['trend.product'].create({
            'name': 'Produit direct',
            'product_ref': 'TEST-AD-LINK-0004',
            'source': 'api',
        })
        ad = self.env['trend.ad'].create({
            'ad_ref': 'AD-REF-0004',
            'product_id': product.id,
            'country': 'MA',
            'social_network': 'facebook',
        })
        self.assertEqual(ad.product_id, product)


class TestTrendAdRequiredFields(TransactionCase):
    """Champs obligatoires de trend.ad : ad_ref, country, social_network."""

    def _base_vals(self, **overrides):
        vals = {
            'ad_ref': 'AD-REF-REQUIRED',
            'country': 'MA',
            'social_network': 'facebook',
        }
        vals.update(overrides)
        return vals

    @mute_logger('odoo.sql_db')
    def test_missing_social_network_raises(self):
        # social_network est required=True : Odoo laisse passer la valeur
        # jusqu'au SQL (pas de ValidationError ORM ici) et c'est la
        # contrainte NOT NULL de la table qui bloque la création.
        with self.assertRaises(Exception):
            self.env['trend.ad'].create(self._base_vals(social_network=False))

    def test_valid_minimal_ad_is_created(self):
        ad = self.env['trend.ad'].create(self._base_vals())
        self.assertTrue(ad.id)
        self.assertEqual(ad.likes_count, 0)
        self.assertEqual(ad.shares_count, 0)
