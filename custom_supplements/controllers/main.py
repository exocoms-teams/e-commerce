from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain

import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleSupplements(WebsiteSale):
    """Keep supplement filters compatible with the native Odoo shop flow."""

    def _get_shop_domain(self, search, category, attrib_values, search_in_description=True, **kwargs):
        _logger.warning('starting _get_search_domain')
        domain = super()._get_shop_domain(
            search, category, attrib_values, search_in_description, **kwargs
        )
        _logger.warning('initial domain : %s', domain)


        # Filtre Vegan
        if request.httprequest.args.get('vegan'):
            # Utilisation standard Odoo 19+
            domain = Domain(domain) & Domain([('is_vegan', '=', True)])

            _logger.warning('vegan domain : %s', domain)
        
        # Filtre Allergènes
        allergen_ids = [
            int(value)
            for value in request.httprequest.args.getlist('allergens_exclude')
            if value.isdigit()
        ]

        if allergen_ids:
            domain &= ~Domain([
                ('allergen_ids', 'in', allergen_ids)
            ])
        
            _logger.warning('allergen domain : %s', domain)


            products = request.env['product.template'].search(domain)

        _logger.warning("DOMAIN : %s", domain)
        _logger.warning("PRODUCTS : %s", products)
        _logger.warning("VEGAN VALUES : %s", products.mapped('is_vegan'))
        return domain

    def _shop_lookup_products(self, options, post, search, website):
        fuzzy_search_term, product_count, search_result = super()._shop_lookup_products(
            options, post, search, website
        )

        # Filtre vegan
        if request.httprequest.args.get('vegan'):
            search_result = search_result.filtered(lambda p: p.is_vegan)

        # Filtre allergènes
        allergen_ids = [
            int(value)
            for value in request.httprequest.args.getlist('allergens_exclude')
            if value.isdigit()
        ]

        if allergen_ids:
            search_result = search_result.filtered(
                lambda p: not (p.allergen_ids.ids and set(p.allergen_ids.ids) & set(allergen_ids))
            )

        product_count = len(search_result)

        return fuzzy_search_term, product_count, search_result
    

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

