from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class TelecomController(http.Controller):

    _STRINGS = {
        'fr_FR': {
            'page_title': 'Solutions Télécom',
            'page_subtitle': (
                'Voix, mobilité, intelligence conversationnelle, '
                'connectivité et cybersécurité pour les professionnels.'
            ),
            'voir_service': 'Voir le service',
        },
        'en_US': {
            'page_title': 'Telecom Solutions',
            'page_subtitle': (
                'Voice, mobility, conversational intelligence, '
                'connectivity and cybersecurity for professionals.'
            ),
            'voir_service': 'View service',
        },
    }

    @http.route('/telecom', type='http', auth='public', website=True)
    def telecom_page(self, **kwargs):
        ProductCateg = request.env['product.public.category'].sudo()
        ProductTemplate = request.env['product.template'].sudo()

        root_categ = request.env.ref(
            'telecom_services.categ_telecom', raise_if_not_found=False
        )

        universes = []
        if root_categ:
            subcategories = ProductCateg.search(
                [('parent_id', '=', root_categ.id)],
                order='sequence, name'
            )
            for categ in subcategories:
                products = ProductTemplate.search([
                    ('public_categ_ids', 'in', categ.ids),
                    ('is_published', '=', True),
                    ('sale_ok', '=', True),
                ])
                universes.append({
                    'category': categ,
                    'products': products,
                })

        lang = request.env.context.get('lang', 'fr_FR')
        strings = self._STRINGS.get(lang, self._STRINGS['fr_FR'])

        return request.render('telecom_services.telecom_page', {
            'universes': universes,
            **strings,
        })


class TelecomShopOverride(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(
            search, category, attrib_values, search_in_description
        )
        return domain + self._telecom_exclusion_domain()

    def _telecom_exclusion_domain(self):
        root_categ = request.env.ref(
            'telecom_services.categ_telecom', raise_if_not_found=False
        )
        if not root_categ:
            return []
        telecom_categs = request.env['product.public.category'].sudo().search(
            [('id', 'child_of', root_categ.id)]
        )
        if not telecom_categs:
            return []
        return [('public_categ_ids', 'not in', telecom_categs.ids)]
