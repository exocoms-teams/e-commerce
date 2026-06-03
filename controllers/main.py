# -*- coding: utf-8 -*-
import datetime
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class MonetiqueWebsite(Website):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
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

    @http.route('/paiement', type='http', auth='public', website=True)
    def payment_page(self, **kwargs):
        return request.render('monetique_theme.page_paiement', {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': False,
        })

    @http.route('/paiement/traiter', type='http', auth='public', website=True,
                 methods=['POST'], csrf=True)
    def process_payment(self, **post):
        try:
            first_name = post.get('first_name', '').strip()
            last_name = post.get('last_name', '').strip()
            email = post.get('email', '').strip()
            phone = post.get('phone', '').strip()
            amount = post.get('amount', '0').strip()
            card_number = post.get('card_number', '').strip()
            card_expiry = post.get('card_expiry', '').strip()
            card_cvv = post.get('card_cvv', '').strip()
            address = post.get('address', '').strip()
            city = post.get('city', '').strip()
            zip_code = post.get('zip_code', '').strip()

            if not (first_name and last_name and email and amount and card_number and card_expiry and card_cvv):
                return request.render('monetique_theme.page_paiement', {
                    'year': datetime.datetime.now().year,
                    'error': True,
                    'error_msg': 'Tous les champs obligatoires doivent être remplis',
                    'form_data': post,
                })

            if '@' not in email:
                return request.render('monetique_theme.page_paiement', {
                    'year': datetime.datetime.now().year,
                    'error': True,
                    'error_msg': 'Email invalide',
                    'form_data': post,
                })

            payment_vals = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'amount': float(amount),
                'address': address,
                'city': city,
                'zip_code': zip_code,
                'payment_date': datetime.datetime.now(),
                'status': 'pending',
                'card_last_4': card_number[-4:],
            }

            payment_record = request.env['payment.transaction'].sudo().create(payment_vals)

            mail_vals = {
                'subject': '[monetiques.fr] Confirmation de paiement',
                'body_html': """
                    <p>Bonjour <strong>%s %s</strong>,</p>
                    <p>Votre paiement de <strong>%.2f €</strong> a été reçu.</p>
                    <p>Référence de transaction: <strong>%s</strong></p>
                    <p>Nous vous remercions de votre confiance.</p>
                    <p>Cordialement,<br/>L'équipe Monetiques</p>
                """ % (first_name, last_name, float(amount), payment_record.id),
                'email_from': request.website.email or 'contact@monetiques.fr',
                'email_to': email,
            }
            request.env['mail.mail'].sudo().create(mail_vals).send()

            return request.render('monetique_theme.page_paiement_success', {
                'year': datetime.datetime.now().year,
                'transaction_id': payment_record.id,
                'amount': float(amount),
            })

        except Exception as e:
            return request.render('monetique_theme.page_paiement', {
                'year': datetime.datetime.now().year,
                'error': True,
                'error_msg': 'Une erreur est survenue lors du traitement du paiement',
                'form_data': post,
            })
