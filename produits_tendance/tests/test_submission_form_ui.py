from odoo.tests.common import HttpCase


class TestSubmissionFormUI(HttpCase):
    """WIN-105 : habillage charte graphique de /submit-trend."""

    def test_submit_trend_page_uses_shared_components(self):
        response = self.url_open('/submit-trend')
        self.assertEqual(response.status_code, 200)
        body = response.text
        self.assertIn('o_winners_card', body)
        self.assertIn('o_winners_btn_primary', body)
        self.assertIn('o_winners_submission_form__input', body)

    def test_submit_trend_success_message_uses_shared_card(self):
        response = self.url_open('/submit-trend?success=1')
        self.assertEqual(response.status_code, 200)
        body = response.text
        self.assertIn('o_winners_submission_form__success', body)
        self.assertIn('Merci pour votre contribution', body)
