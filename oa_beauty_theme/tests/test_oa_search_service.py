from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestOASearchService(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['oa.search.service']
        cls.category = cls.env['product.public.category'].create({'name': 'Skincare'})
        cls.fragrance_category = cls.env['product.public.category'].create({'name': 'Fragrances'})
        cls.serum = cls.env['product.template'].create({
            'name': 'Sérum Glow Vitamin C',
            'sale_ok': True,
            'is_published': True,
            'list_price': 49.0,
            'public_categ_ids': [(6, 0, [cls.category.id])],
            'description_sale': 'A radiant serum for dry and sensitive skin.',
            'oa_type': 'Sérum',
            'oa_best_for': 'Peau sèche, peau sensible',
            'oa_key_ingredients': 'Vitamine C, acide hyaluronique',
            'oa_benefits': '<p>Hydratation et éclat.</p>',
            'oa_seo_keywords': 'serum, vitamin c, dry skin',
        })
        cls.perfume = cls.env['product.template'].create({
            'name': 'Velvet Floral Eau de Parfum',
            'sale_ok': True,
            'is_published': True,
            'list_price': 89.0,
            'public_categ_ids': [(6, 0, [cls.fragrance_category.id])],
            'description_sale': 'A floral perfume.',
            'oa_type': 'Eau de Parfum',
            'oa_fragrance_top_notes': 'Bergamote',
            'oa_fragrance_heart_notes': 'Rose, jasmin',
            'oa_fragrance_base_notes': 'Musc, vanille',
            'oa_mood': 'Floral, romantique',
        })
        cls.unpublished = cls.env['product.template'].create({
            'name': 'Hidden Hydrating Cream',
            'sale_ok': True,
            'is_published': False,
            'list_price': 29.0,
            'oa_type': 'Crème hydratante',
        })

    def _ids_for(self, query):
        return [item['id'] for item in self.service.search_products(query, limit=10)['results']]

    def test_exact_and_partial_search(self):
        self.assertEqual(self._ids_for('Sérum Glow')[0], self.serum.id)
        self.assertIn(self.serum.id, self._ids_for('ser'))

    def test_category_ingredient_and_concern_search(self):
        self.assertIn(self.serum.id, self._ids_for('skincare'))
        self.assertIn(self.serum.id, self._ids_for('vitamin C'))
        self.assertIn(self.serum.id, self._ids_for('peau sèche'))

    def test_fragrance_search(self):
        self.assertIn(self.perfume.id, self._ids_for('floral perfume'))
        self.assertIn(self.perfume.id, self._ids_for('عطر زهري'))

    def test_multilingual_accent_and_typo_tolerance(self):
        self.assertIn(self.serum.id, self._ids_for('serum for dry skin'))
        self.assertIn(self.serum.id, self._ids_for('سيروم'))
        self.assertIn('hydratation', self.service.expand_terms('hydratnt'))
        self.assertIn(self.serum.id, self._ids_for('hydratnt'))
        self.assertEqual(self.service.normalize_query('SÉRUM   peau sèche'), 'serum peau seche')

    def test_zero_result_and_unpublished_exclusion(self):
        self.assertFalse(self._ids_for('xxxxxnotfound'))
        self.assertNotIn(self.unpublished.id, self._ids_for('hidden hydrating cream'))
