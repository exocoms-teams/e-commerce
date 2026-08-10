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


class TestKeyIndicatorsBanner(TransactionCase):
    """WIN-104 : bandeau d'indicateurs clés sous le hero.

    template_key_indicators est paramétré (total_products/avg_score fournis
    par l'appelant) et n'accède jamais à `request` : testable directement en
    lui passant des valeurs explicites, sans dépendre de l'état réel de la
    base ni d'un contexte HTTP - même principe que template_how_it_works.
    """

    def test_key_indicators_renders_given_values(self):
        html = self.env['ir.qweb']._render(
            'produits_tendance.template_key_indicators',
            {'total_products': 42, 'avg_score': 67.8},
        )
        body = str(html)
        self.assertIn('o_winners_key_indicators', body)
        self.assertIn('42', body)
        self.assertIn('67.8', body)

    def test_key_indicators_has_three_tiles(self):
        html = self.env['ir.qweb']._render(
            'produits_tendance.template_key_indicators',
            {'total_products': 0, 'avg_score': 0.0},
        )
        body = str(html)
        self.assertEqual(body.count('o_winners_stat_tile__label'), 3)
