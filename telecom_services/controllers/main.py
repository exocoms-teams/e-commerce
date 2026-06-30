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

# Ordered KISSGROUP catalogue sections shown on /telecom, with their label.
_KISSGROUP_SECTIONS = [
    ('mobile_plan', 'Mobile'),
    ('sim_pack', 'Cartes SIM'),
]


class TelecomController(http.Controller):

    @http.route('/telecom', type='http', auth='public', website=True)
    def telecom_page(self, **kwargs):
        lang = request.env.context.get('lang', 'fr_FR')
        strings = _UI_STRINGS.get(lang, _UI_STRINGS['fr_FR'])

        return request.render('telecom_services.telecom_page', {
            'universes': self._kissgroup_universes(),
            **strings,
        })

    def _kissgroup_universes(self):
        Product = request.env['product.template'].sudo()
        universes = []
        for kind, label in _KISSGROUP_SECTIONS:
            products = Product.search([
                ('kissgroup_kind', '=', kind),
                ('is_published', '=', True),
            ], order='list_price, name')
            if not products:
                continue
            universes.append({
                'id': kind,
                'category': label,
                'products': [{
                    'name': p.name,
                    'description': p.description_sale,
                    'price': p.list_price,
                    'url': p.website_url,
                } for p in products],
            })
        return universes


class TelecomShopOverride(WebsiteSale):

    def _get_search_domain(self, *args, **kwargs):
        domain = super()._get_search_domain(*args, **kwargs)
        # KISSGROUP products are sold only on /telecom, never in /shop.
        return domain + [('is_telecom_only', '!=', True)]
