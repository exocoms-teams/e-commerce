# -*- coding: utf-8 -*-
import logging
import re

from markupsafe import Markup
from odoo import http
from odoo.http import request

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
_logger = logging.getLogger(__name__)


class MatelasVente(http.Controller):

    def _partner_has_purchased(self, partner):
        """Return whether the partner has at least one confirmed order."""
        return bool(request.env['sale.order'].sudo().search_count([
            ('partner_id', '=', partner.id),
            ('state', '=', 'sale'),
        ], limit=1))

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

        # Fallback volontaire : la seconde requête n’est exécutée que si
        # aucun produit publié avec le tag Nouveauté n’a été trouvé.
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
        user = request.env.user
        public_user = request.env.ref('base.public_user')
        user_connected = user.id != public_user.id
        a_achete = (
            self._partner_has_purchased(user.partner_id)
            if user_connected else False
        )
        avis_list = request.env['matelas.avis'].sudo().search([
            ('is_published', '=', True),
        ], order='create_date desc', limit=20)

        return request.render('matelas.avis_page', {
            'a_achete': a_achete,
            'user_connected': user_connected,
            'avis_list': avis_list,
        })

    @http.route('/avis/submit', type='jsonrpc', auth='user', website=True)
    def avis_submit(self, name=None, note=None, titre=None, commentaire=None, profession=None, **kwargs):
        partner = request.env.user.partner_id

        if not self._partner_has_purchased(partner):
            return {
                'success': False,
                'error': "Vous devez avoir effectué un achat pour laisser un avis.",
            }

        name = (name or '').strip()
        profession = (profession or '').strip()
        titre = (titre or '').strip()
        commentaire = (commentaire or '').strip()

        try:
            note = int(note)
        except (TypeError, ValueError):
            note = 0

        if (
            not name
            or not titre
            or not commentaire
            or note not in range(1, 6)
        ):
            return {
                'success': False,
                'error': "Merci de remplir tous les champs obligatoires.",
            }
        request.env['matelas.avis'].sudo().create({
            'name': name,
            'profession': profession,
            'note': note,
            'titre': titre,
            'commentaire': commentaire,
            'partner_id': partner.id,
        })

        return {'success': True}

    @http.route('/contact', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('matelas.contact_page', {})
    @http.route('/contact/submit', type='jsonrpc', auth='public', website=True,)
    def contact_submit(
        self,
        nom=None,
        prenom=None,
        email=None,
        telephone=None,
        sujet=None,
        message=None,
        website=None,
        **kwargs,
    ):
        """Enregistrer un message de contact et avertir la société par email."""
        nom = (nom or '').strip()
        prenom = (prenom or '').strip()
        email = (email or '').strip()
        telephone = (telephone or '').strip()
        sujet = (sujet or '').strip()
        message = (message or '').strip()
        website = (website or '').strip()

        # Honeypot anti-spam : ce champ reste vide pour un utilisateur normal.
        if website:
            return {
                'success': False,
                'error': "La soumission du formulaire a été refusée.",
            }

        if not nom or not prenom or not email or not message:
            return {
                'success': False,
                'error': "Merci de remplir tous les champs obligatoires.",
            }

        if not EMAIL_REGEX.match(email):
            return {
                'success': False,
                'error': "L'adresse email saisie est invalide.",
            }

        if (
            len(nom) > 100
            or len(prenom) > 100
            or len(email) > 254
            or len(telephone) > 50
            or len(sujet) > 200
            or len(message) > 5000
        ):
            return {
                'success': False,
                'error': "Certaines informations saisies sont trop longues.",
            }

        company = request.env.company.sudo()
        email_to = (company.email or '').strip()

        if not email_to or not EMAIL_REGEX.match(email_to):
            _logger.error(
                "Impossible d'envoyer le formulaire de contact : "
                "aucune adresse email valide n'est configurée sur la société."
            )
            return {
                'success': False,
                'error': (
                    "Le service de contact est temporairement indisponible."
                ),
            }

        clean_subject = sujet.replace('\r', ' ').replace('\n', ' ')
        mail_subject = "Nouveau message de contact"
        if clean_subject:
            mail_subject = f"{mail_subject} - {clean_subject}"

        body_html = Markup("""
            <p>Un nouveau message a été envoyé depuis le site Matelas.</p>
            <table>
                <tr><th align="left">Nom</th><td>{}</td></tr>
                <tr><th align="left">Prénom</th><td>{}</td></tr>
                <tr><th align="left">Email</th><td>{}</td></tr>
                <tr><th align="left">Téléphone</th><td>{}</td></tr>
                <tr><th align="left">Sujet</th><td>{}</td></tr>
            </table>
            <p><strong>Message :</strong></p>
            <div style="white-space: pre-wrap;">{}</div>
        """).format(
            nom,
            prenom,
            email,
            telephone or "Non renseigné",
            sujet or "Non renseigné",
            message,
        )

        try:
            # Le point de sauvegarde garantit qu'aucun message incomplet
            # n'est conservé si la création ou l'envoi de l'email échoue.
            with request.env.cr.savepoint():
                request.env['matelas.contact_message'].sudo().create({
                    'nom': nom,
                    'prenom': prenom,
                    'email': email,
                    'telephone': telephone,
                    'sujet': sujet,
                    'message': message,
                })

                mail = request.env['mail.mail'].sudo().create({
                    'subject': mail_subject,
                    'email_from': (
                        company.partner_id.email_formatted or email_to
                    ),
                    'email_to': email_to,
                    'reply_to': email,
                    'body_html': body_html,
                    'auto_delete': True,
                })
                mail.send(raise_exception=True)
        except Exception:
            _logger.exception(
                "Échec du traitement du formulaire de contact."
            )
            return {
                'success': False,
                'error': (
                    "Une erreur est survenue pendant l'envoi du message."
                ),
            }

        return {'success': True}

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