# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PayCoreWebsite(http.Controller):
    """
    Controller principal du site PayCore.
    Gère toutes les routes publiques du site vitrine.
    """

    @http.route('/', type='http', auth='public', website=True)
    def home(self, **kwargs):
        values = self._get_base_values()
        values.update({
            'page_title': 'PayCore — Infrastructure de Paiement Moderne',
            'meta_description': (
                'Solutions monétiques professionnelles : TPE, encaissement, '
                'paiement omnicanal, maintenance et support technique. '
                'Infrastructure de paiement sécurisée pour entreprises françaises.'
            ),
            'og_title': 'PayCore — Solutions Monétiques & Paiement',
        })
        return request.render('paycore_website.page_home', values)

    @http.route('/services', type='http', auth='public', website=True)
    def services(self, **kwargs):
        values = self._get_base_values()
        values.update({
            'page_title': 'Nos Services — PayCore',
            'meta_description': (
                'Découvrez l\'ensemble de nos services : monétique, encaissement, '
                'TPE, support technique, maintenance préventive et corrective.'
            ),
        })
        return request.render('paycore_website.page_services', values)

    @http.route('/solutions/tpe', type='http', auth='public', website=True)
    def tpe(self, **kwargs):
        values = self._get_base_values()
        values.update({
            'page_title': 'Solutions TPE — PayCore',
            'meta_description': (
                'Terminaux de paiement professionnels : TPE fixes, mobiles, Android. '
                'Installation, configuration, formation et maintenance incluses.'
            ),
        })
        return request.render('paycore_website.page_tpe', values)

    @http.route('/solutions/encaissement', type='http', auth='public', website=True)
    def encaissement(self, **kwargs):
        values = self._get_base_values()
        values.update({
            'page_title': 'Solutions d\'Encaissement — PayCore',
            'meta_description': (
                'Systèmes d\'encaissement complets pour commerces, restaurants et retail. '
                'Caisse enregistreuse connectée, logiciels de caisse certifiés NF525.'
            ),
        })
        return request.render('paycore_website.page_encaissement', values)

    @http.route('/solutions/paiement-omnicanal', type='http', auth='public', website=True)
    def omnicanal(self, **kwargs):
        values = self._get_base_values()
        values.update({
            'page_title': 'Paiement Omnicanal — PayCore',
            'meta_description': (
                'Acceptez les paiements partout : en magasin, en ligne, sur mobile. '
                'Unifiez votre infrastructure de paiement avec PayCore.'
            ),
        })
        return request.render('paycore_website.page_omnicanal', values)

    @http.route('/support', type='http', auth='public', website=True)
    def support(self, **kwargs):
        values = self._get_base_values()
        values.update({
            'page_title': 'Support Technique — PayCore',
            'meta_description': (
                'Support technique 7j/7, interventions sur site, maintenance préventive '
                'et corrective. SLA garanti pour votre infrastructure de paiement.'
            ),
        })
        return request.render('paycore_website.page_support', values)

    @http.route('/a-propos', type='http', auth='public', website=True)
    def about(self, **kwargs):
        values = self._get_base_values()
        values.update({
            'page_title': 'À Propos — PayCore',
            'meta_description': (
                'PayCore, spécialiste français de la monétique depuis 2005. '
                'Notre mission : simplifier et sécuriser votre infrastructure de paiement.'
            ),
        })
        return request.render('paycore_website.page_about', values)

    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        values = self._get_base_values()
        values.update({
            'page_title': 'Contact — PayCore',
            'meta_description': 'Contactez nos experts en monétique et solutions de paiement.',
        })
        return request.render('paycore_website.page_contact', values)

    @http.route('/contact/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def contact_submit(self, **post):
        """Traitement du formulaire de contact."""
        name = post.get('name', '').strip()
        email = post.get('email', '').strip()
        company = post.get('company', '').strip()
        phone = post.get('phone', '').strip()
        subject = post.get('subject', '').strip()
        message = post.get('message', '').strip()

        if name and email and message:
            # Créer un lead/ticket dans Odoo
            vals = {
                'name': f"Contact site — {subject or name}",
                'partner_name': name,
                'email_from': email,
                'mobile': phone,
                'description': f"Société : {company}\n\n{message}",
                'tag_ids': [],
            }
            try:
                request.env['crm.lead'].sudo().create(vals)
            except Exception:
                # CRM pas installé : envoi email fallback
                mail_vals = {
                    'subject': f'[PayCore Contact] {subject or name}',
                    'body_html': (
                        f'<p><b>Nom :</b> {name}</p>'
                        f'<p><b>Email :</b> {email}</p>'
                        f'<p><b>Société :</b> {company}</p>'
                        f'<p><b>Tél :</b> {phone}</p>'
                        f'<p><b>Message :</b><br/>{message}</p>'
                    ),
                    'email_to': 'contact@paycore.fr',
                    'email_from': email,
                }
                request.env['mail.mail'].sudo().create(mail_vals).send()

        return request.redirect('/contact?sent=1')

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_base_values(self):
        """Valeurs communes injectées dans tous les templates."""
        return {
            'page_title': 'PayCore',
            'meta_description': 'Infrastructure de paiement moderne pour entreprises.',
            'og_title': 'PayCore',
            'og_description': 'Solutions monétiques et paiement professionnel.',
        }
