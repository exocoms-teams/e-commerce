# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlencode

from odoo import http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class ExocomsSignupRequestHome(AuthSignupHome):
    """Inscription portail en deux temps.

    Le formulaire public ne collecte que le nom et l'adresse email, et
    n'enregistre qu'une ligne dans ``exocoms.signup.request``. Le clic sur le
    lien reçu crée le contact, prépare un jeton d'invitation Odoo et bascule
    sur ``/web/signup?token=...``, c'est-à-dire sur le parcours **natif** :
    c'est Odoo qui crée l'utilisateur, enregistre le mot de passe et ouvre la
    session.

    Aucune manipulation du cycle de vie de ``res.users`` n'a donc lieu ici.
    """

    @staticmethod
    def _exocoms_values(**overrides):
        """Contexte de rendu complet.

        QWeb lève une exception sur toute variable absente du contexte : chaque
        clé utilisée par les templates doit donc être fournie systématiquement,
        y compris sur les requêtes GET où aucune erreur n'est possible.
        """
        values = {'email': '', 'name': '', 'error': '', 'resent': False,
                  'state': ''}
        values.update(overrides)
        return values

    # ==================================================================
    # Formulaire public
    # ==================================================================
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        # Parcours par invitation (back-office, ou retour de confirmation) :
        # strictement natif, on ne s'en mêle pas.
        if request.params.get('token'):
            return super().web_auth_signup(*args, **kw)

        if not self._exocoms_signup_open():
            return request.redirect('/web/login')

        values = self._exocoms_values(
            email=(kw.get('email') or kw.get('login') or '').strip(),
            name=(kw.get('name') or '').strip(),
        )

        if request.httprequest.method == 'POST':
            # Piège à robots : ce champ est masqué et n'est jamais rempli par
            # un humain. On répond la page de confirmation habituelle plutôt
            # qu'une erreur, pour ne pas indiquer au robot qu'il a été repéré.
            if (kw.get('website_url') or '').strip():
                _logger.info("Dépôt d'inscription ignoré (piège à robots)")
                return request.redirect('/signup/pending')
            try:
                request.env['exocoms.signup.request'].sudo()._submit(
                    email=values['email'],
                    name=values['name'],
                    base_url=self._exocoms_base_url(),
                    website=getattr(request, 'website', None),
                    lang=request.env.context.get('lang'),
                    ip_address=self._exocoms_remote_addr(),
                )
                return request.redirect('/signup/pending?%s' % urlencode({
                    'email': values['email'].strip().lower(),
                }))
            except UserError as error:
                values['error'] = error.args[0]
            except Exception:  # noqa: BLE001
                _logger.exception("Échec de dépôt d'une demande d'inscription")
                values['error'] = (
                    "Une erreur technique est survenue. Merci de réessayer "
                    "dans quelques instants.")

        return request.render('exocoms_signup_request.request_form', values)

    def _exocoms_signup_open(self):
        """L'inscription libre est-elle autorisée sur cette base ?"""
        scope = request.env['ir.config_parameter'].sudo().get_param(
            'auth_signup.invitation_scope', 'b2b')
        return scope == 'b2c'

    def _exocoms_remote_addr(self):
        """Adresse IP d'origine, transmise au modèle pour empreinte.

        Elle n'est ni stockée ni journalisée : le modèle n'en conserve qu'un
        HMAC. Derrière le proxy d'Odoo.sh, cette valeur n'est correcte que si
        le serveur tourne en mode proxy (`--proxy-mode`), ce qui est le cas par
        défaut sur la plateforme.
        """
        try:
            return request.httprequest.remote_addr or ''
        except Exception:  # noqa: BLE001
            return ''

    def _exocoms_base_url(self):
        """Racine d'URL du site sur lequel la demande est déposée."""
        website = getattr(request, 'website', None)
        if website and website.domain:
            domain = website.domain.strip()
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://%s' % domain
            return domain
        return request.httprequest.url_root

    # ==================================================================
    # Pages de suivi
    # ==================================================================
    @http.route('/signup/pending', type='http', auth='public', website=True,
                sitemap=False)
    def exocoms_signup_pending(self, **kw):
        return request.render(
            'exocoms_signup_request.request_pending',
            self._exocoms_values(email=(kw.get('email') or '').strip()))

    @http.route('/signup/confirm/<string:token>', type='http', auth='public',
                website=True, sitemap=False)
    def exocoms_signup_confirm(self, token, **kw):
        Requests = request.env['exocoms.signup.request'].sudo()
        state, record = Requests._confirm_token(token)

        if state == 'done':
            partner = record.partner_id

            if partner and not partner.user_ids:
                ttl_hours = Requests._get_int_param(
                    'token_ttl_hours',
                    company=record.company_id,
                )
                signup_token = partner.sudo()._generate_signup_token(
                    expiration=ttl_hours
                )
                return request.redirect('/web/signup?%s' % urlencode({
                    'token': signup_token,
                }))

            # Cas limite : le contact existe déjà avec un compte actif.
            return request.redirect('/web/login?%s' % urlencode({
                'login': record.email,
            }))

        return request.render(
            'exocoms_signup_request.request_confirm_failed',
            self._exocoms_values(
                state=state, email=record.email if record else ''))


    @http.route('/signup/resend', type='http', auth='public', website=True,
                methods=['POST'], sitemap=False)
    def exocoms_signup_resend(self, **kw):
        email = (kw.get('email') or '').strip().lower()
        Requests = request.env['exocoms.signup.request'].sudo()
        website = getattr(request, 'website', None)
        company = website.company_id if website else request.env.company
        record = Requests._find_pending(email, company=company)
        error = ''
        if record:
            try:
                # Contrôle avant régénération : un renvoi refusé ne doit pas
                # invalider le lien déjà en circulation.
                record._check_resend_allowed()
                record._refresh_token(base_url=self._exocoms_base_url())
                record._send_confirmation_email()
            except UserError as exc:
                error = exc.args[0]
        return request.render(
            'exocoms_signup_request.request_pending',
            self._exocoms_values(email=email, error=error, resent=not error))
