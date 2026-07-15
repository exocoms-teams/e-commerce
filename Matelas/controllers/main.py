# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class MatelasVente(http.Controller):

    @http.route('/', auth='public', website=True)
    def index(self, **kwargs):
        products = request.env['product.template'].sudo().search([
            ('is_published', '=', True)
        ], limit=6)

        
        nouveaute_tag = request.env.ref(
            'Matelas.product_tag_nouveaute', raise_if_not_found=False)

        nouveautes = request.env['product.template']
        if nouveaute_tag:
            nouveautes = request.env['product.template'].sudo().search([
                ('is_published', '=', True),
                ('product_tag_ids', 'in', nouveaute_tag.ids),
            ], limit=6)

        if not nouveautes:

            nouveautes = request.env['product.template'].sudo().search([
                ('is_published', '=', True),
            ], order='create_date desc', limit=6)

        temoignages = request.env['matelas.avis'].sudo().search([
            ('is_published', '=', True),
        ], order='note desc, create_date desc', limit=30)

        return request.render('Matelas.home', {
            'products': products,
            'nouveautes': nouveautes,
            'temoignages': temoignages,
        })

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

        avis_list = request.env['matelas.avis'].sudo().search([
            ('is_published', '=', True),
        ], order='create_date desc', limit=20)

        return request.render('Matelas.avis_page', {
            'a_achete': a_achete,
            'user_connected': request.env.user.id != request.env.ref('base.public_user').id,
            'avis_list': avis_list,
        })

    @http.route('/avis/submit', type='jsonrpc', auth='user', website=True)
    def avis_submit(self, name=None, note=None, titre=None, commentaire=None, **kwargs):
        partner = request.env.user.partner_id

        commandes = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', 'in', ['sale', 'done']),
        ], limit=1)
        if not commandes:
            return {
                'success': False,
                'error': "Vous devez avoir effectué un achat pour laisser un avis.",
            }

        if not name or not (commentaire and commentaire.strip()) or not note:
            return {
                'success': False,
                'error': "Merci de remplir tous les champs obligatoires.",
            }

        try:
            note = int(note)
        except (TypeError, ValueError):
            note = 0
        note = max(1, min(5, note))

        request.env['matelas.avis'].sudo().create({
            'name': name,
            'note': note,
            'titre': titre or '',
            'commentaire': commentaire,
            'partner_id': partner.id,
        })

        return {'success': True}

    @http.route('/contact', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('Matelas.contact_page', {})

    @http.route('/mentions-legales', auth='public', website=True)
    def mentions_legales(self, **kwargs):
        return request.render('Matelas.mentions_legales', {})

    @http.route('/produit/<model("product.template"):product>/fiche', auth='public', website=True, sitemap=False)
    def fiche_technique(self, product, **kwargs):
        return request.render('Matelas.fiche_technique', {
            'product': product,
        })