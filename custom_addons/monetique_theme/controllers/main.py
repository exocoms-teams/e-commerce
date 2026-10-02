from odoo import http
from odoo.http import request
import logging
import uuid

_logger = logging.getLogger(__name__)


class Monetique(http.Controller):

    # ── ACCUEIL ──────────────────────────────────────────────────────
    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        return request.render('monetique_theme.page_home', {})

    # ── NOS SERVICES ─────────────────────────────────────────────────
    @http.route('/nos-services', type='http', auth='public', website=True, sitemap=True)
    def nos_services(self, **kw):
        return request.render('sinistre_services.page_nos_services', {})

    # ── URGENCE ──────────────────────────────────────────────────────
    @http.route('/urgence', type='http', auth='public', website=True, sitemap=True)
    def urgence(self, **kw):
        return request.render('sinistre_services.page_urgence', {})

    # ── DEMANDE D'INTERVENTION ───────────────────────────────────────
    @http.route('/demande-intervention', type='http', auth='public', website=True, sitemap=True)
    def demande_intervention(self, **kw):
        return request.render('sinistre_services.page_demande', {
            'type_pre': kw.get('type', ''),
            'urgence_pre': kw.get('urgence', ''),
            'error': False, 'success': False, 'reference': None, 'form_data': {},
        })

    # Route /demande-intervention/send gérée par sinistre_services
    # (website_controller.py) : création de la mission + compte client.

    # Routes /rejoindre-le-reseau gérées par sinistre_services/controllers/website_controller.py

    # ── ASSURANCES ───────────────────────────────────────────────────
    @http.route('/assurances', type='http', auth='public', website=True, sitemap=True)
    def assurances(self, **kw):
        return request.render('sinistre_services.page_assurances', {})

    @http.route('/assurances/api-access', type='http', auth='public', website=True, sitemap=True)
    def api_access(self, **kw):
        return request.render('sinistre_services.page_api_access', {
            'error': False, 'success': False, 'form_data': {},
        })

    @http.route('/assurances/api-access/send', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def api_access_send(self, **post):
        societe = post.get('societe', '').strip()
        email = post.get('email', '').strip()
        nom = post.get('nom', '').strip()

        if not (societe and email and nom):
            return request.render('sinistre_services.page_api_access', {
                'error': True, 'success': False, 'form_data': post,
            })

        try:
            token_api = str(uuid.uuid4())[:8].upper()
            mail_vals = {
                'subject': f'[API Sinistres] Demande acces — {societe}',
                'body_html': f'''
                    <h3>Demande d\'acces API Assureur</h3>
                    <p><b>Societe :</b> {societe}</p>
                    <p><b>Nom :</b> {nom}</p>
                    <p><b>Email :</b> {email}</p>
                    <p><b>Tel :</b> {post.get("telephone", "Non renseigne")}</p>
                    <p><b>Volume :</b> {post.get("volume", "Non renseigne")}</p>
                    <p><b>Systeme :</b> {post.get("systeme", "Non renseigne")}</p>
                    <p><b>Besoins :</b> {post.get("besoins", "")}</p>
                    <p><i>Token provisoire : {token_api}</i></p>
                ''',
                'email_from': email,
                'email_to': request.website.email or 'api@sinistre-services.fr',
            }
            request.env['mail.mail'].sudo().create(mail_vals).send()
        except Exception as e:
            _logger.warning(f"API access send failed: {e}")

        return request.render('sinistre_services.page_api_access', {
            'error': False, 'success': True, 'form_data': {},
        })

    # ── CONTACT ──────────────────────────────────────────────────────
    @http.route('/contact', type='http', auth='public', website=True, sitemap=True)
    def contact(self, **kw):
        return request.render('sinistre_services.page_contact', {
            'error': False, 'success': False, 'form_data': {},
        })

    @http.route('/contact/send', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def contact_send(self, **post):
        name = post.get('name', '').strip()
        email = post.get('email', '').strip()
        message = post.get('message', '').strip()

        if not (name and email and message):
            return request.render('sinistre_services.page_contact', {
                'error': True, 'success': False, 'form_data': post,
            })

        try:
            mail_vals = {
                'subject': f"[Contact] {post.get('sujet', 'Nouveau message')}",
                'body_html': f'''
                    <p><b>Nom :</b> {name}</p>
                    <p><b>Email :</b> {email}</p>
                    <p><b>Tel :</b> {post.get("phone", "Non renseigne")}</p>
                    <p><b>Message :</b><br/>{message}</p>
                ''',
                'email_from': email,
                'email_to': request.website.email or 'contact@sinistre-services.fr',
            }
            request.env['mail.mail'].sudo().create(mail_vals).send()
        except Exception as e:
            _logger.warning(f"Contact send failed: {e}")

        return request.render('sinistre_services.page_contact', {
            'error': False, 'success': True, 'form_data': {},
        })

    # Route /suivi/<token> gérée par sinistre_services (website_controller.py).

    # ── RAPPEL ───────────────────────────────────────────────────────
    @http.route('/rappel', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def rappel(self, **post):
        phone = post.get('phone', '').strip()
        name = post.get('name', '').strip()
        if phone:
            try:
                mail_vals = {
                    'subject': '[Sinistre Services] Demande de rappel',
                    'body_html': f'<p><b>Nom :</b> {name or "Non renseigne"}</p>'
                                 f'<p><b>Tel :</b> {phone}</p>',
                    'email_from': request.website.email or 'noreply@sinistre-services.fr',
                    'email_to': request.website.email or 'contact@sinistre-services.fr',
                }
                request.env['mail.mail'].sudo().create(mail_vals).send()
            except Exception as e:
                _logger.warning(f"Rappel failed: {e}")
        return request.redirect('/?rappel=ok')

    # ── ESPACE ARTISAN ────────────────────────────────────────────────
    @http.route('/intervenant/login', type='http', auth='public', website=True, sitemap=False)
    def intervenant_login(self, **kw):
        """Page de connexion espace artisan avec theme Monetique bleu."""
        return request.render('sinistre_services.page_intervenant_login', {})
