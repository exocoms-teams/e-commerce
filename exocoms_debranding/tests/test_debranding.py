# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

from ..tools.debrand import debrand_html

SNIPPET = '<span>Propulsé par <a href="https://exocoms.fr">EXOCOMS</a></span>'

PDF_FOOTER = (
    '<div class="text-center" style="font-size:8px;">'
    '<span>Powered by</span> '
    '<a target="_blank" href="https://www.odoo.com?utm_source=db">'
    '<span style="color:#875A7B;">Odoo</span></a></div>'
)


@tagged("post_install", "-at_install")
class TestDebranding(TransactionCase):

    # --- mode suppression -------------------------------------------------
    def test_remove_report_footer(self):
        self.assertEqual(debrand_html(PDF_FOOTER), "")

    def test_remove_keeps_sibling_content(self):
        html = (
            '<td><p>ACME SAS, 1 rue de Paris</p>'
            '<div>Powered by <a href="https://www.odoo.com">Odoo</a></div></td>'
        )
        result = debrand_html(html)
        self.assertIn("ACME SAS", result, "l'adresse société doit être conservée")
        self.assertNotIn("odoo", result.lower())

    def test_remove_sent_by_using(self):
        html = 'Sent by <span>ACME</span> using <a href="http://odoo.com">Odoo</a>'
        self.assertNotIn("odoo", debrand_html(html).lower())

    # --- mode remplacement ------------------------------------------------
    def test_replace_keeps_container(self):
        result = debrand_html(PDF_FOOTER, snippet=SNIPPET, generator="EXOCOMS")
        self.assertIn('class="text-center"', result)
        self.assertIn("EXOCOMS", result)
        self.assertNotIn("odoo.com", result)

    def test_replace_injects_once(self):
        html = (
            '<div>Powered by <a href="https://odoo.com">Odoo</a></div>'
            '<footer><div>Powered by <a href="https://odoo.com">Odoo</a></div></footer>'
        )
        result = debrand_html(html, snippet="<span>BRAND</span>")
        self.assertEqual(result.count("BRAND"), 1, "une seule injection par document")
        self.assertNotIn("odoo", result.lower())

    def test_meta_generator_renamed(self):
        html = '<head><meta name="generator" content="Odoo"/></head>'
        self.assertIn("EXOCOMS", debrand_html(html, generator="EXOCOMS"))

    # --- absence de faux positifs ----------------------------------------
    def test_other_brands_untouched(self):
        for html in (
            "<p>Powered by Stripe Connect</p>",
            "<p>Sent by Marie using our internal tool</p>",
            "<p>Envoyé par Radia avec accusé de réception</p>",
            "<p>Bonjour, voici votre devis S00042.</p>",
        ):
            self.assertEqual(debrand_html(html, snippet=SNIPPET), html)

    # --- intégration ------------------------------------------------------
    def test_company_snippet(self):
        company = self.env.company
        company.write({
            "debrand_mode": "replace",
            "debrand_promo_text": "Propulsé par",
            "debrand_brand_name": "EXOCOMS Group",
            "debrand_brand_url": "https://exocoms.fr",
            "debrand_show_logo": False,
        })
        snippet = company._debrand_snippet()
        self.assertIn("EXOCOMS Group", snippet)
        self.assertIn("https://exocoms.fr", snippet)
        company.debrand_mode = "remove"
        self.assertIsNone(company._debrand_snippet())

    def test_qweb_render_is_debranded(self):
        self.env.company.write({
            "debrand_mode": "replace",
            "debrand_brand_name": "EXOCOMS Group",
            "debrand_show_logo": False,
        })
        view = self.env["ir.ui.view"].create({
            "name": "exocoms debrand test",
            "type": "qweb",
            "key": "exocoms_debranding.test_tpl",
            "arch_db": (
                '<t t-name="exocoms_debranding.test_tpl">'
                '<div>Devis<div>Powered by '
                '<a href="https://www.odoo.com">Odoo</a></div></div></t>'
            ),
        })
        rendered = str(self.env["ir.qweb"]._render(view.id))
        self.assertIn("Devis", rendered)
        self.assertIn("EXOCOMS Group", rendered)
        self.assertNotIn("odoo.com", rendered)
