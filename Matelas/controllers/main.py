# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class MatelasVente(http.Controller):

    @http.route('/', auth='public', website=True)
    def index(self, **kwargs):
        products = request.env['product.template'].sudo().search([
            ('is_published', '=', True)
        ], limit=6)
        return request.render('Matelas.home', {'products': products})
    
    @http.route('/avis', auth='public', website=True)
    def avis(self, **kwargs):
       return request.render('Matelas.avis_page', {})
    
    @http.route('/contact', auth='public', website=True)
    def contact(self, **kwargs):
       return request.render('Matelas.contact_page', {})