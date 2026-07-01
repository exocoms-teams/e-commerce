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
        partner = request.env.user.partner_id
        a_achete = False

        if request.env.user.id != request.env.ref('base.public_user').id:
            commandes = request.env['sale.order'].sudo().search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done']),
            ], limit=1)
            a_achete = bool(commandes)

        return request.render('Matelas.avis_page', {
            'a_achete': a_achete,
            'user_connected': request.env.user.id != request.env.ref('base.public_user').id,
        })

    @http.route('/contact', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('Matelas.contact_page', {})

    @http.route('/mentions-legales', auth='public', website=True)
    def mentions_legales(self, **kwargs):
        return request.render('Matelas.mentions_legales', {})