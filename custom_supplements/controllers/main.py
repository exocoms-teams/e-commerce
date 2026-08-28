from odoo import http,Domain
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleSupplements(WebsiteSale):
    """Keep supplement filters compatible with the native Odoo shop flow."""

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True, **kwargs):
        domain = super()._get_search_domain(
            search, category, attrib_values, search_in_description, **kwargs
        )

        # Filtre Vegan
        if request.httprequest.args.get('vegan'):
            # Utilisation standard Odoo 19+
            domain = Domain(domain) & Domain([('is_vegan', '=', True)])

        
        # Filtre Allergènes
        allergen_ids = [
            int(value)
            for value in request.httprequest.args.getlist('allergens_exclude')
            if value.isdigit()
        ]

        if allergen_ids:
            domain = Domain(domain) & Domain([('allergen_ids', 'not in', allergen_ids)])
        

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
        allergens_exclude_ids = [
            int(value)
            for value in request.httprequest.args.getlist('allergens_exclude')
            if value.isdigit()
        ]
        values = super()._get_additional_shop_values(values, **kwargs)
        values['supplement_vegan'] = bool(request.httprequest.args.get('vegan'))
        values['allergens'] = request.env['allergen'].sudo().search([])
        values['allergens_exclude_ids'] = allergens_exclude_ids
        return values

