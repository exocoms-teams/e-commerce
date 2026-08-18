# -*- coding: utf-8 -*-
import re

from odoo import http
from odoo.http import request

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


class MatelasVente(http.Controller):
    """Controleur du site principal, Matelas."""

    @http.route('/', auth='public', website=True)
    def index(self, **kwargs):
        products = request.env['product.template'].sudo().search([
            ('is_published', '=', True)
        ], limit=4)

        nouveaute_tag = request.env.ref(
            'matelas.product_tag_nouveaute', raise_if_not_found=False)

        nouveautes = request.env['product.template']
        if nouveaute_tag:
            nouveautes = request.env['product.template'].sudo().search([
                ('is_published', '=', True),
                ('product_tag_ids', 'in', nouveaute_tag.ids),
            ], limit=4)

        if not nouveautes:
            nouveautes = request.env['product.template'].sudo().search([
                ('is_published', '=', True),
            ], order='create_date desc', limit=4)

        temoignages = request.env['matelas.avis'].sudo().search([
            ('is_published', '=', True),
        ], order='note desc, create_date desc', limit=30)

        return request.render('matelas.home', {
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

        return request.render('matelas.avis_page', {
            'a_achete': a_achete,
            'user_connected': request.env.user.id != request.env.ref('base.public_user').id,
            'avis_list': avis_list,
        })

    @http.route('/avis/submit', type='jsonrpc', auth='user', website=True)
    def avis_submit(self, name=None, note=None, titre=None, commentaire=None, profession=None, **kwargs):
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
            'profession': profession or '',
            'note': note,
            'titre': titre or '',
            'commentaire': commentaire,
            'partner_id': partner.id,
        })

        return {'success': True}

    @http.route('/contact', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('matelas.contact_page', {})

    @http.route('/mentions-legales', auth='public', website=True)
    def mentions_legales(self, **kwargs):
        return request.render('matelas.mentions_legales', {})

    @http.route('/produit/<model("product.template"):product>/fiche', auth='public', website=True, sitemap=False)
    def fiche_technique(self, product, **kwargs):
        return request.render('matelas.fiche_technique', {
            'product': product,
        })

    @http.route('/newsletter/subscribe', type='jsonrpc', auth='public', website=True)
    def newsletter_subscribe(self, value=None, **kwargs):
        """Inscription à la newsletter : la liste de diffusion est résolue
        ici côté serveur (via son external id) plutôt que d'être injectée
        dynamiquement dans le HTML, pour que le bloc newsletter reste un
        bloc 100% statique (donc éditable via le Website Builder)."""
        email = (value or '').strip()
        if not email or not EMAIL_REGEX.match(email):
            return {'success': False, 'error': "Adresse email invalide."}

        mailing_list = request.env.ref(
            'matelas.newsletter_mailing_list', raise_if_not_found=False)
        if not mailing_list:
            return {'success': False, 'error': "Liste de diffusion introuvable."}

        Contacts = request.env['mailing.contact'].sudo()
        Subscriptions = request.env['mailing.subscription'].sudo()

        subscription = Subscriptions.search([
            ('list_id', '=', mailing_list.id),
            ('contact_id.email', '=', email),
        ], limit=1)

        if not subscription:
            contact = Contacts.search([('email', '=', email)], limit=1)
            if not contact:
                contact = Contacts.create({
                    'name': email.split('@')[0],
                    'email': email,
                })
            Subscriptions.create({
                'contact_id': contact.id,
                'list_id': mailing_list.id,
            })
        elif subscription.opt_out:
            subscription.opt_out = False

        return {'success': True}