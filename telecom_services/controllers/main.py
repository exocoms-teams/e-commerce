from odoo import http
from odoo.http import request


class TelecomController(http.Controller):

    @http.route('/telecom', type='http', auth='public', website=True)
    def telecom_page(self, **kwargs):
        ProductCateg = request.env['product.public.category'].sudo()
        ProductTemplate = request.env['product.template'].sudo()

        root_categ = ProductCateg.search(
            [('name', '=', 'Télécom'), ('parent_id', '=', False)],
            limit=1
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

        return request.render('telecom_services.telecom_page', {
            'universes': universes,
        })
