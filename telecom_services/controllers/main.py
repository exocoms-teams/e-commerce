from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_UI_STRINGS = {
    'fr_FR': {
        'page_title': 'Solutions Télécom',
        'page_subtitle': (
            'Voix, mobilité, intelligence conversationnelle, '
            'connectivité et cybersécurité pour les professionnels.'
        ),
    },
    'en_US': {
        'page_title': 'Telecom Solutions',
        'page_subtitle': (
            'Voice, mobility, conversational intelligence, '
            'connectivity and cybersecurity for professionals.'
        ),
    },
}


class TelecomController(http.Controller):

    @http.route('/telecom', type='http', auth='public', website=True)
    def telecom_page(self, **kwargs):
        lang = request.env.context.get('lang', 'fr_FR')
        strings = _UI_STRINGS.get(lang, _UI_STRINGS['fr_FR'])

        root = request.env.ref(
            'telecom_services.categ_telecom', raise_if_not_found=False
        )
        universes = []
        if root:
            subcategories = request.env['product.public.category'].sudo().search(
                [('parent_id', '=', root.id)],
                order='sequence, name',
            )
            for categ in subcategories:
                products = request.env['product.template'].sudo().search([
                    ('public_categ_ids', 'in', categ.ids),
                    ('is_published', '=', True),
                ])
                if products:
                    universes.append({'category': categ, 'products': products})

        return request.render('telecom_services.telecom_page', {
            'universes': universes,
            **strings,
        })


class TelecomShopOverride(WebsiteSale):

    def _get_search_domain(self, *args, **kwargs):
        domain = super()._get_search_domain(*args, **kwargs)
        return domain + self._telecom_exclusion_domain()

    def _telecom_exclusion_domain(self):
        root = request.env.ref(
            'telecom_services.categ_telecom', raise_if_not_found=False
        )
        if not root:
            return []
        categs = request.env['product.public.category'].sudo().search(
            [('id', 'child_of', root.id)]
        )
        if not categs:
            return []
        return [('public_categ_ids', 'not in', categs.ids)]
