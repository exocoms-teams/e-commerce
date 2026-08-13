from odoo.tests.common import TransactionCase


class TestEmptyStateTemplate(TransactionCase):
    """WIN-123 : structure standard des pages "coquilles" de navigation
    (Alertes, Collections, Favoris, Historique, Comparaison, Analytics).

    Comme template_how_it_works (WIN-103) et template_key_indicators
    (WIN-104), on teste directement le sous-template paramétré
    (template_empty_state) plutôt que les 6 templates de page : ces
    derniers héritent de website.layout, indisponible en TransactionCase
    (AttributeError sur request, cf. test_homepage.py).
    """

    def _render(self, **values):
        return str(self.env['ir.qweb']._render('produits_tendance.template_empty_state', values))

    def test_renders_title_and_text(self):
        body = self._render(
            icon='fa-bell-o',
            title='Aucune alerte pour le moment',
            text='Texte de test.',
            action_label=False,
        )
        self.assertIn('o_winners_empty_state', body)
        self.assertIn('Aucune alerte pour le moment', body)
        self.assertIn('Texte de test.', body)

    def test_no_action_button_when_action_label_false(self):
        body = self._render(
            icon='fa-star-o',
            title='Aucun favori pour le moment',
            text='Texte de test.',
            action_label=False,
        )
        self.assertNotIn('o_winners_empty_state__action', body)
        self.assertNotIn('o_winners_coming_soon_btn', body)

    def test_action_button_shown_when_action_label_set(self):
        body = self._render(
            icon='fa-folder-o',
            title='Vous n’avez pas encore de collection',
            text='Texte de test.',
            action_label='+ Nouvelle collection',
        )
        self.assertIn('o_winners_empty_state__action', body)
        self.assertIn('o_winners_coming_soon_btn', body)
        self.assertIn('+ Nouvelle collection', body)

    def test_icon_class_is_applied(self):
        body = self._render(
            icon='fa-history',
            title='Aucun historique pour le moment',
            text='Texte de test.',
            action_label=False,
        )
        self.assertIn('fa fa-history o_winners_empty_state__icon', body)
