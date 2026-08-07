from odoo.tests.common import HttpCase


class TestHomepageHowItWorks(HttpCase):
    """WIN-103 : section "Comment ça marche" sous le hero de la landing page."""

    def test_homepage_renders_how_it_works_section(self):
        response = self.url_open('/')
        self.assertEqual(response.status_code, 200)
        body = response.text
        self.assertIn('o_winners_how_it_works', body)
        self.assertIn('Comment ça marche', body)

    def test_homepage_how_it_works_has_three_steps(self):
        response = self.url_open('/')
        body = response.text
        self.assertEqual(body.count('o_winners_how_it_works__step_title'), 3)
