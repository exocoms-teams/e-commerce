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

    @http.route('/demande-intervention/send', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def demande_send(self, **post):
        nom = post.get('nom', '').strip()
        telephone = post.get('telephone', '').strip()
        type_intervention = post.get('type_intervention', '').strip()
        adresse = post.get('adresse', '').strip()
        description = post.get('description', '').strip()

        if not (telephone and type_intervention and adresse):
            return request.render('sinistre_services.page_demande', {
                'error': True, 'success': False, 'form_data': post,
                'type_pre': '', 'urgence_pre': '', 'reference': None,
            })

        reference = None
        try:
            client = request.env['res.partner'].sudo().create({
                'name': nom or 'Client Web',
                'phone': telephone,
                'email': post.get('email', ''),
            })
            mission = request.env['sinistre.mission'].sudo().create({
                'source': post.get('source', 'particulier'),
                'client_id': client.id,
                'type_intervention': type_intervention,
                'urgence': post.get('urgence', 'normale'),
                'description_sinistre': description,
                'adresse_intervention': adresse,
                'tel_sur_place': telephone,
                'state': 'nouveau',
            })
            reference = mission.reference

            mail_vals = {
                'subject': f'[Sinistre Services] Nouvelle demande {reference}',
                'body_html': f'''
                    <h3>Nouvelle demande d\'intervention</h3>
                    <p><b>Reference :</b> {reference}</p>
                    <p><b>Client :</b> {nom or "Non renseigne"}</p>
                    <p><b>Tel :</b> {telephone}</p>
                    <p><b>Type :</b> {type_intervention}</p>
                    <p><b>Urgence :</b> {post.get("urgence", "normale")}</p>
                    <p><b>Adresse :</b> {adresse}</p>
                    <p><b>Description :</b> {description}</p>
                ''',
                'email_from': request.website.email or 'noreply@sinistre-services.fr',
                'email_to': request.website.email or 'contact@sinistre-services.fr',
            }
            request.env['mail.mail'].sudo().create(mail_vals).send()
        except Exception as e:
            _logger.warning(f"Demande send failed: {e}")

        return request.render('sinistre_services.page_demande', {
            'error': False, 'success': True,
            'reference': reference,
            'type_pre': '', 'urgence_pre': '', 'form_data': {},
        })

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

    # ── SUIVI DOSSIER ────────────────────────────────────────────────
    @http.route('/suivi/<string:token>', type='http', auth='public', website=True)
    def suivi_dossier(self, token, **kw):
        mission = request.env['sinistre.mission'].sudo().search(
            [('token_api', '=', token)], limit=1)
        if not mission:
            return request.render('sinistre_services.page_404', {
                'message': "Dossier introuvable. Verifiez le lien recu.",
            })
        return request.render('sinistre_services.page_suivi', {'mission': mission})

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
