# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class MatelasVente(http.Controller):

    @http.route('/', auth='public', website=True)
    def index(self, **kwargs):
        products = request.env['product.template'].sudo().search([
            ('is_published', '=', True)
        ], limit=3)
        return request.render('Matelas.home', {'products': products})