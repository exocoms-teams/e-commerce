from odoo.tests.common import TransactionCase


class TestHomepageHowItWorks(TransactionCase):
    """WIN-103 : section "Comment ça marche" sous le hero de la landing page.

    Rendu du sous-template dédié (template_how_it_works) plutôt que la
    homepage complète : ce sous-template n'a aucune dépendance à
    website.layout/request (contrairement à website.homepage, testé et
    confirmé indisponible en TransactionCase - AttributeError sur
    request.env.user quand aucune requête HTTP n'est active), donc
    directement testable ici, comme template_product_cards pour le
    dashboard. Evite aussi le conflit de route '/' avec le controleur de
    monetique_theme (un autre projet client partageant ce bac a sable
    Odoo.sh, sans rapport avec produits_tendance).
    """

    def test_how_it_works_section_present(self):
        html = self.env['ir.qweb']._render('produits_tendance.template_how_it_works')
        body = str(html)
        self.assertIn('o_winners_how_it_works', body)
        self.assertIn('Comment ça marche', body)

    def test_how_it_works_has_three_steps(self):
        html = self.env['ir.qweb']._render('produits_tendance.template_how_it_works')
        body = str(html)
        self.assertEqual(body.count('o_winners_how_it_works__step_title'), 3)
