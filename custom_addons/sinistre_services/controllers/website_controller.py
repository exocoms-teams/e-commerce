# -*- coding: utf-8 -*-
"""
Contrôleur Website public — Sinistre Services
Adapté de monetique_theme/controllers/main.py

Routes :
  /                           → Page d'accueil
  /nos-services               → Présentation des services
  /urgence                    → Page urgence 24/7
  /demande-intervention       → Formulaire demande (particulier / entreprise)
  /demande-intervention/send  → Traitement POST formulaire
  /contact                    → Formulaire contact
  /contact/send               → Traitement POST contact
  /suivi/<token>              → Suivi dossier public par token UUID
  /rappel                     → POST modal rappel
"""
import datetime
import logging

from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class SinistreWebsite(http.Controller):

    # ─── ACCUEIL ────────────────────────────────────────────────────
    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        return request.render('sinistre_services.ss_homepage', {
            'year': datetime.datetime.now().year,
        })

    # ─── NOS SERVICES ───────────────────────────────────────────────
    @http.route('/nos-services', type='http', auth='public', website=True)
    def nos_services(self, **kwargs):
        return request.render('sinistre_services.ss_page_services', {
            'year': datetime.datetime.now().year,
        })

    # ─── URGENCE 24/7 ───────────────────────────────────────────────
    @http.route('/urgence', type='http', auth='public', website=True)
    def urgence(self, **kwargs):
        return request.render('sinistre_services.ss_page_urgence', {
            'year': datetime.datetime.now().year,
        })

    # ─── FORMULAIRE DE DEMANDE D'INTERVENTION ───────────────────────
    @http.route('/demande-intervention', type='http', auth='public', website=True)
    def demande_intervention(self, **kwargs):
        """Formulaire de prise de contact / demande directe."""
        success = kwargs.get('success', False)
        return request.render('sinistre_services.ss_page_demande', {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': success,
            'form_data': {},
        })

    @http.route('/demande-intervention/send', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def demande_send(self, **post):
        """Traitement du formulaire de demande d'intervention."""
        # Validation basique
        required = ['nom', 'email', 'telephone', 'type_intervention', 'adresse', 'description']
        if not all(post.get(f, '').strip() for f in required):
            return request.render('sinistre_services.ss_page_demande', {
                'year': datetime.datetime.now().year,
                'error': True,
                'success': False,
                'form_data': post,
            })

        source = post.get('source', 'particulier')
        if source not in ('particulier', 'entreprise'):
            source = 'particulier'

        # Créer ou trouver le partenaire
        env = request.env(su=True)
        email = post.get('email', '').strip()
        partner = env['res.partner'].search([('email', '=', email)], limit=1)
        if not partner:
            is_company = (source == 'entreprise')
            name_parts = [post.get('prenom', '').strip(), post.get('nom', '').strip()]
            if is_company and post.get('entreprise_nom', '').strip():
                full_name = post.get('entreprise_nom', '').strip()
            else:
                full_name = ' '.join(p for p in name_parts if p) or post.get('nom', 'Client').strip()
            partner = env['res.partner'].create({
                'name': full_name,
                'email': email,
                'phone': post.get('telephone', '').strip(),
                'is_company': is_company,
            })

        # Créer la mission
        try:
            mission = env['sinistre.mission'].create({
                'source': source,
                'client_id': partner.id,
                'type_intervention': post.get('type_intervention', 'autre'),
                'urgence': post.get('urgence', 'normale'),
                'description_sinistre': post.get('description', ''),
                'adresse_intervention': post.get('adresse', ''),
                'contact_sur_place': f"{post.get('prenom', '')} {post.get('nom', '')}".strip(),
                'tel_sur_place': post.get('telephone', ''),
                'commentaire_interne': post.get('commentaire', ''),
            })
            _logger.info(f"[WEBSITE] Nouvelle demande créée : {mission.reference} ({source})")
        except Exception as e:
            _logger.error(f"[WEBSITE] Erreur création mission web: {e}")
            return request.render('sinistre_services.ss_page_demande', {
                'year': datetime.datetime.now().year,
                'error': True,
                'success': False,
                'form_data': post,
            })

        # Notification email interne
        try:
            mail_vals = {
                'subject': f'[Sinistre Services] Nouvelle demande {source} — {mission.reference}',
                'body_html': f"""
                    <p><strong>Référence :</strong> {mission.reference}</p>
                    <p><strong>Source :</strong> {source}</p>
                    <p><strong>Type :</strong> {post.get('type_intervention', '')}</p>
                    <p><strong>Urgence :</strong> {post.get('urgence', 'normale')}</p>
                    <p><strong>Client :</strong> {partner.name} — {email} — {post.get('telephone', '')}</p>
                    <p><strong>Adresse :</strong> {post.get('adresse', '')}</p>
                    <p><strong>Description :</strong><br/>{post.get('description', '')}</p>
                """,
                'email_from': email,
                'email_to': request.website.email or 'contact@sinistre-services.fr',
            }
            env['mail.mail'].create(mail_vals).send()
        except Exception as e:
            _logger.warning(f"Email notification failed: {e}")

        return request.render('sinistre_services.ss_page_demande', {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': True,
            'reference': mission.reference,
            'token': mission.token_api,
            'form_data': {},
        })

    # ─── CONTACT ────────────────────────────────────────────────────
    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('sinistre_services.ss_page_contact', {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': False,
            'form_data': {},
        })

    @http.route('/contact/send', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def contact_send(self, **post):
        name = post.get('name', '').strip()
        email = post.get('email', '').strip()
        message = post.get('message', '').strip()

        if not (name and email and message):
            return request.render('sinistre_services.ss_page_contact', {
                'year': datetime.datetime.now().year,
                'error': True,
                'success': False,
                'form_data': post,
            })

        try:
            mail_vals = {
                'subject': f"[Contact] {post.get('sujet', 'Nouveau message')}",
                'body_html': f"""
                    <p><strong>Nom :</strong> {name}</p>
                    <p><strong>Email :</strong> {email}</p>
                    <p><strong>Téléphone :</strong> {post.get('phone', 'Non renseigné')}</p>
                    <p><strong>Message :</strong><br/>{message}</p>
                """,
                'email_from': email,
                'email_to': request.website.email or 'contact@sinistre-services.fr',
            }
            request.env['mail.mail'].sudo().create(mail_vals).send()
        except Exception as e:
            _logger.warning(f"Contact send failed: {e}")

        return request.render('sinistre_services.ss_page_contact', {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': True,
            'form_data': {},
        })

    # ─── SUIVI DOSSIER (token public) ───────────────────────────────
    @http.route('/suivi/<string:token>', type='http', auth='public', website=True)
    def suivi_dossier(self, token, **kwargs):
        """Suivi public d'une mission par token UUID — sans authentification."""
        mission = request.env['sinistre.mission'].sudo().search([
            ('token_api', '=', token),
        ], limit=1)

        if not mission:
            return request.render('sinistre_services.ss_page_404', {
                'year': datetime.datetime.now().year,
                'message': "Dossier introuvable. Vérifiez le lien reçu par email.",
            })

        return request.render('sinistre_services.ss_page_suivi', {
            'year': datetime.datetime.now().year,
            'mission': mission,
        })

    # ─── MODAL RAPPEL ───────────────────────────────────────────────
    @http.route('/rappel', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def rappel(self, **post):
        phone = post.get('phone', '').strip()
        name = post.get('name', '').strip()
        if phone:
            try:
                mail_vals = {
                    'subject': '[Sinistre Services] Demande de rappel',
                    'body_html': f'<p><strong>Nom :</strong> {name or "Non renseigné"}</p>'
                                 f'<p><strong>Téléphone :</strong> {phone}</p>',
                    'email_from': request.website.email or 'contact@sinistre-services.fr',
                    'email_to': request.website.email or 'contact@sinistre-services.fr',
                }
                request.env['mail.mail'].sudo().create(mail_vals).send()
            except Exception as e:
                _logger.warning(f"Rappel mail failed: {e}")
        return request.redirect('/?rappel=ok')

    # ── Demande d'accès API sandbox (formulaire assurance) ────────────
    @http.route('/assurances/api-access', type='http', auth='public',
                website=True, methods=['GET'], csrf=False)
    def api_access_form(self, **kw):
        return request.render('sinistre_services.ss_page_api_access', {
            'error': False, 'success': False,
            'year': datetime.datetime.now().year,
        })

    @http.route('/assurances/api-access/send', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def api_access_send(self, **post):
        societe = post.get('societe', '').strip()
        nom     = post.get('nom', '').strip()
        email   = post.get('email', '').strip()

        if not societe or not nom or not email:
            return request.render('sinistre_services.ss_page_api_access', {
                'error': True, 'success': False, 'year': datetime.datetime.now().year,
            })

        env = request.env(su=True)

        # Vérifier si assurance déjà existante
        existing = env['sinistre.assurance'].search(
            [('partner_id.email', '=', email)], limit=1
        )
        if existing:
            # Déjà inscrit — afficher succès quand même (sécurité)
            return request.render('sinistre_services.ss_page_api_access', {
                'error': False, 'success': True, 'year': datetime.datetime.now().year,
            })

        # Créer le partenaire
        partner = env['res.partner'].search([('email', '=', email)], limit=1)
        if not partner:
            partner = env['res.partner'].create({
                'name':         societe,
                'email':        email,
                'phone':        post.get('telephone', '').strip(),
                'company_type': 'company',
            })

        # Types de sinistres cochés
        types = []
        for t in ['serrurerie', 'plomberie', 'vitrerie', 'menuiserie', 'electricite']:
            if post.get(f'type_{t}'):
                types.append(t)

        # Créer la fiche assurance
        note = f"Contact: {nom}\nVolume: {post.get('volume','')}\nSystème: {post.get('systeme','')}\nTypes: {', '.join(types)}\nBesoins: {post.get('besoins','')}"
        assurance = env['sinistre.assurance'].create({
            'name':          societe,
            'partner_id':    partner.id,
            'statut_compte': 'en_attente',
            'note':          note,
        })

        # Notifier l'admin par email
        try:
            admin = env.ref('base.user_admin')
            env['mail.mail'].create({
                'subject':    f"Nouvelle demande d'accès API — {societe}",
                'email_to':   admin.email or 'admin@sinistre-services.fr',
                'email_from': 'no-reply@sinistre-services.fr',
                'body_html':  f"""
                    <h3>Nouvelle demande sandbox API</h3>
                    <p><b>Société :</b> {societe}</p>
                    <p><b>Contact :</b> {nom}</p>
                    <p><b>Email :</b> {email}</p>
                    <p><b>Téléphone :</b> {post.get('telephone','')}</p>
                    <p><b>Volume :</b> {post.get('volume','')}</p>
                    <p><b>Types :</b> {', '.join(types)}</p>
                    <p><b>Besoins :</b> {post.get('besoins','')}</p>
                    <p><a href="/odoo/sinistre/assurances/{assurance.id}">Valider le compte dans Odoo →</a></p>
                """,
            }).send()
        except Exception:
            pass

        return request.render('sinistre_services.ss_page_api_access', {
            'error': False, 'success': True, 'year': datetime.datetime.now().year,
        })
