# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestNewsletterWizard(TransactionCase):
    """Vérifie que la newsletter (rendue via le template QWeb
    matelas.mail_template_newsletter) se génère correctement avec 0, 1 et
    plusieurs produits (cas limites)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # On dépublie les produits déjà présents (démo) pour contrôler
        # précisément le nombre de produits vus par le wizard à chaque test.
        cls.env['product.template'].search([('is_published', '=', True)]).write({
            'is_published': False,
        })
        cls.nouveaute_tag = cls.env.ref(
            'matelas.product_tag_nouveaute', raise_if_not_found=False)

    def _make_product(self, name, price=100.0):
        vals = {
            'name': name,
            'list_price': price,
            'is_published': True,
        }
        if self.nouveaute_tag:
            vals['product_tag_ids'] = [(6, 0, self.nouveaute_tag.ids)]
        return self.env['product.template'].create(vals)

    def _generate(self):
        wizard = self.env['matelas.newsletter.wizard'].create({})
        wizard.action_generate()
        return self.env['mailing.mailing'].search([], order='id desc', limit=1)

    def test_zero_produits(self):
        """Cas limite : aucun produit publié -> le template se rend quand
        même (structure générale présente, aucune ligne produit)."""
        mailing = self._generate()
        self.assertIn('MATELAS', mailing.body_html)
        self.assertNotIn('image_256', mailing.body_html)

    def test_un_produit(self):
        """Cas limite : un seul produit -> une seule ligne produit."""
        self._make_product("Matelas Test Solo")
        mailing = self._generate()
        self.assertIn("Matelas Test Solo", mailing.body_html)
        self.assertEqual(mailing.body_html.count('image_256'), 1)

    def test_six_produits(self):
        """Cas nominal : plusieurs produits -> autant de lignes produit
        (la recherche du wizard est limitée à 6)."""
        for i in range(6):
            self._make_product("Matelas Test %s" % i)
        mailing = self._generate()
        for i in range(6):
            self.assertIn("Matelas Test %s" % i, mailing.body_html)
        self.assertEqual(mailing.body_html.count('image_256'), 6)
