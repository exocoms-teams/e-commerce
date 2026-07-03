# -*- coding: utf-8 -*-
import datetime
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class MonetiqueWebsite(Website):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
    # Redirection automatique si un module sidebar EXOCOMS est installé
        IrModule = request.env['ir.module.module'].sudo()
        sidebar_modules = ['exocoms_sidebar_cards', 'exocoms_sidebar_tree', 'exocoms_sidebar_accordion']
        for module_name in sidebar_modules:
            module = IrModule.search([('name', '=', module_name), ('state', '=', 'installed')], limit=1)
            if module:
                return request.redirect('/boutique')

    # Comportement normal monetique
        Product = request.env['product.template'].sudo()
        featured = Product.search([
            ('is_published', '=', True),
            ('website_published', '=', True),
        ], limit=8, order='website_sequence asc')
        return request.render('monetique_theme.homepage', {
            'featured_products': featured,
            'year': datetime.datetime.now().year,
    })

    @http.route('/solutions', type='http', auth='public', website=True)
    def solutions(self, **kwargs):
        return request.render('monetique_theme.page_solutions', {
            'year': datetime.datetime.now().year,
        })

    @http.route('/a-propos', type='http', auth='public', website=True)
    def a_propos(self, **kwargs):
        return request.render('monetique_theme.page_a_propos', {
            'year': datetime.datetime.now().year,
        })

    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('monetique_theme.page_contact', {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': False,
        })

    @http.route('/contact/send', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def contact_send(self, **post):
        name = post.get('name', '').strip()
        email = post.get('email', '').strip()
        phone = post.get('phone', '').strip()
        sujet = post.get('sujet', '').strip()
        message = post.get('message', '').strip()

        if not (name and email and message):
            return request.render('monetique_theme.page_contact', {
                'year': datetime.datetime.now().year,
                'error': True,
                'form_data': post,
            })

        mail_vals = {
            'subject': '[monetiques.fr] %s' % (sujet or 'Nouveau message'),
            'body_html': """
                <p><strong>Nom :</strong> %s</p>
                <p><strong>Email :</strong> %s</p>
                <p><strong>Téléphone :</strong> %s</p>
                <p><strong>Message :</strong><br/>%s</p>
            """ % (name, email, phone or 'Non renseigné', message),
            'email_from': email,
            'email_to': request.website.email or 'contact@monetiques.fr',
        }
        request.env['mail.mail'].sudo().create(mail_vals).send()
        return request.render('monetique_theme.page_contact_success', {
            'year': datetime.datetime.now().year,
        })

    @http.route('/rappel', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def rappel(self, **post):
        phone = post.get('phone', '').strip()
        name = post.get('name', '').strip()
        if phone:
            mail_vals = {
                'subject': '[monetiques.fr] Demande de rappel',
                'body_html': '<p><strong>Nom :</strong> %s</p><p><strong>Téléphone :</strong> %s</p>' % (name or 'Non renseigné', phone),
                'email_from': request.website.email or 'contact@monetiques.fr',
                'email_to': request.website.email or 'contact@monetiques.fr',
            }
            request.env['mail.mail'].sudo().create(mail_vals).send()
        return request.redirect('/?rappel=ok')
