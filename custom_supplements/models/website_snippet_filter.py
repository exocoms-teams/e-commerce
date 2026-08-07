from odoo import models
from odoo.osv.expression import Domain

class WebsiteSnippetFilter(models.Model):
    _inherit = "website.snippet.filter"

    def _get_products_alternative_products(
        self, website, limit, domain, product_template_id=None, **kwargs,
    ):
        domain = Domain(domain) & Domain('free_qty', '>', 0)
        products = super()._get_products_alternative_products(
            website,
            limit,
            domain,
            product_template_id=product_template_id,
            **kwargs,
        )

        