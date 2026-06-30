from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_UI_STRINGS = {
    'fr_FR': {
        'page_title': 'Solutions Télécom',
        'page_subtitle': 'Nos offres télécom pour les professionnels.',
    },
    'en_US': {
        'page_title': 'Telecom Solutions',
        'page_subtitle': 'Our telecom offers for professionals.',
    },
}


class TelecomController(http.Controller):

    @http.route('/telecom', type='http', auth='public', website=True)
    def telecom_page(self, **kwargs):
        lang = request.env.context.get('lang', 'fr_FR')
        strings = _UI_STRINGS.get(lang, _UI_STRINGS['fr_FR'])

        universes = []
        mobile_universe = self._kissgroup_mobile_universe()
        if mobile_universe:
            universes.append(mobile_universe)

        return request.render('telecom_services.telecom_page', {
            'universes': universes,
            **strings,
        })

    def _kissgroup_mobile_universe(self):
        products = request.env['product.template'].sudo().search([
            ('kissgroup_plan_code', '!=', False),
            ('is_published', '=', True),
        ], order='list_price, name')
        if not products:
            return None
        return {
            'id': 'mobile-kissgroup',
            'category': 'Mobile',
            'products': [{
                'name': p.name,
                'description': p.description_sale,
                'price': p.list_price,
                'url': p.website_url,
            } for p in products],
        }


class TelecomShopOverride(WebsiteSale):

    def _get_search_domain(self, *args, **kwargs):
        domain = super()._get_search_domain(*args, **kwargs)
        # KISSGROUP products are sold only on /telecom, never in /shop.
        return domain + [('is_telecom_only', '!=', True)]
