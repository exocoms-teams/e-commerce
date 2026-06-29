# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class TelecomController(http.Controller):

    @http.route('/telecom', type='http', auth='public', website=True, sitemap=True)
    def telecom_page(self, **kwargs):
        """
        Catalogue télécom groupé par univers.
        sudo() justifié : lecture de données catalogue publiques,
        même pattern que /shop dans website_sale.
        """
        # Catégorie racine du catalogue télécom
        telecom_root = request.env['product.public.category'].sudo().search([
            ('name', '=', 'Télécom'),
            ('parent_id', '=', False),
        ], limit=1)

        universes = []
        if telecom_root:
            subcats = request.env['product.public.category'].sudo().search([
                ('parent_id', '=', telecom_root.id),
            ], order='sequence asc, name asc')

            for cat in subcats:
                # Multi-site : request.website est disponible dans le contexte website=True
                products = request.env['product.template'].sudo().search([
                    ('public_categ_ids', 'in', [cat.id]),
                    ('is_published', '=', True),
                    ('sale_ok', '=', True),
                ])
                if products:
                    universes.append({
                        'category': cat,
                        'products': products,
                    })

        return request.render('telecom_services.telecom_page', {
            'universes': universes,
            'page_title': 'Solutions Télécom — Exocoms Group',
        })
