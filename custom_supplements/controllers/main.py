from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain

class WebsiteSaleSupplements(WebsiteSale):
    """Keep supplement filters compatible with the native Odoo shop flow."""

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True, **kwargs):
        domain = super()._get_search_domain(
            search, category, attrib_values, search_in_description, **kwargs
        )
        if request.httprequest.args.get('vegan'):
            # Utilisation standard Odoo 19+
            domain = Domain(domain) & Domain([('is_vegan', '=', True)])
        return domain

    def _get_search_options(self, **kwargs):
        options = super()._get_search_options(**kwargs)
        options['allergens_exclude_ids'] = [
            int(value)
            for value in request.httprequest.args.getlist('allergens_exclude')
            if value.isdigit()
        ]
        return options

    def _get_additional_shop_values(self, values, **kwargs):
        values = super()._get_additional_shop_values(values, **kwargs)
        values['supplement_vegan'] = bool(request.httprequest.args.get('vegan'))
        values['allergens'] = request.env['allergen'].sudo().search([])
        return values

    from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import route, request

