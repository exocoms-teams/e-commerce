from odoo import http
from odoo.http import request


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
