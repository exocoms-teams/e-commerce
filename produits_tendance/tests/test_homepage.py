from odoo.tests.common import TransactionCase


class TestHomepageHowItWorks(TransactionCase):
    """WIN-103 : section "Comment ça marche" sous le hero de la landing page.

    Rendu directement via ir.qweb plutôt qu'un appel HTTP sur '/' : sur ce
    projet, la route '/' est aussi captée par le controleur d'un tout autre
    module (monetique_theme, @http.route('/', ...) dans controllers/main.py
    a la racine du depot) qui prend systematiquement le dessus sur le
    mecanisme standard website.homepage utilise par notre template - un
    conflit entre deux projets clients partageant ce bac a sable Odoo.sh,
    sans rapport avec produits_tendance. Rendre le template directement
    isole le test de ce conflit et teste ce qui nous appartient reellement.
    """

    def test_how_it_works_section_present(self):
        html = self.env['ir.qweb']._render('produits_tendance.homepage')
        body = str(html)
        self.assertIn('o_winners_how_it_works', body)
        self.assertIn('Comment ça marche', body)

    def test_how_it_works_has_three_steps(self):
        html = self.env['ir.qweb']._render('produits_tendance.homepage')
        body = str(html)
        self.assertEqual(body.count('o_winners_how_it_works__step_title'), 3)
