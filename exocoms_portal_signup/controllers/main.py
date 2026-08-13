# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlencode

import werkzeug

from odoo import _, http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class ExocomsAuthSignupHome(AuthSignupHome):
    """Inscription portail : vérification d'adresse puis activation par lien.

    Le point d'entrée principal est ``_signup_with_values()``, appelé par le
    ``do_signup()`` natif **après** la validation Odoo du formulaire. Toute
    cette validation est donc conservée : on n'y touche pas, on se contente de
    remplacer la connexion automatique par l'envoi d'un lien d'activation.
    """

    # ==================================================================
    # Inscription
    # ==================================================================
    def _signup_with_values(self, token, values, *args, **kwargs):
        # Invitation émise depuis le back-office : l'adresse est déjà connue de
        # l'entreprise, on conserve strictement le comportement natif.
        if token:
            return super()._signup_with_values(token, values, *args, **kwargs)
        Users = request.env['res.users'].sudo()
        login = Users._exocoms_check_email(values.get('login'))
        values['login'] = login
        if not values.get('name'):
            values['name'] = login

        base_url = self._exocoms_request_base_url()

        # Inscription déjà déposée mais jamais activée : on relance l'email au
        # lieu de renvoyer « adresse déjà utilisée ». Le nom et le mot de passe
        # soumis sont ignorés — un tiers connaissant l'adresse ne doit pas
        # pouvoir écraser les identifiants d'une inscription en cours. Les
        # quotas s'appliquent, faute de quoi le formulaire deviendrait un
        # outil d'envoi massif contre une adresse tierce.
        pending = Users._exocoms_find_pending(login)
        if pending:
            try:
                pending._exocoms_check_resend_allowed()
                pending._exocoms_prepare_activation(base_url=base_url)
                pending._exocoms_send_activation_email()
            except UserError as exc:
                _logger.info("Relance d'inscription ignorée (%s) : %s", login, exc)
            return True

        Users.signup(values, None)
        request.env.cr.commit()

        user = Users.with_context(active_test=False).search(
            Users._get_login_domain(login), order=Users._get_login_order(), limit=1)
        if not user:
            raise UserError(_("Impossible de créer le compte."))

        user._exocoms_prepare_activation(base_url=base_url)
        # Le compte est sécurisé en base avant l'envoi : une panne SMTP ne doit
        # pas faire perdre l'inscription, le visiteur pourra demander un renvoi.
        request.env.cr.commit()
        try:
            user._exocoms_send_activation_email()
        except Exception:  # noqa: BLE001
            _logger.exception("Envoi de l'email d'activation impossible (%s)", login)
        return True

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        """Orchestration de l'inscription publique.

        La validation du formulaire reste entièrement native : on appelle
        ``do_signup()`` sans le réécrire. Seule la suite change — ni email
        « compte créé » d'Odoo, ni connexion automatique, mais une redirection
        vers la page « vérifiez vos emails ».
        """
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            # Invitation back-office : comportement natif intégral.
            if qcontext.get('token'):
                return super().web_auth_signup(*args, **kw)
            try:
                self.do_signup(qcontext)
                login = (qcontext.get('login') or '').strip().lower()
                return request.redirect('/signup/pending?%s' % urlencode({
                    'login': login,
                }))
            except UserError as error:
                qcontext['error'] = error.args[0]
            except (SignupError, AssertionError) as error:
                exists = request.env['res.users'].sudo().with_context(
                    active_test=False).search_count(
                        [('login', '=', qcontext.get('login'))])
                if exists:
                    qcontext['error'] = _(
                        "Un compte existe déjà avec cette adresse email.")
                else:
                    _logger.warning("Échec d'inscription portail : %s", error)
                    qcontext['error'] = _("Impossible de créer le compte.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    def _exocoms_request_base_url(self):
        """Racine d'URL du site sur lequel la demande a été déposée."""
        website = getattr(request, 'website', None)
        if website and website.domain:
            domain = website.domain.strip()
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://%s' % domain
            return domain
        return request.httprequest.url_root

    # ==================================================================
    # Pages d'activation
    # ==================================================================
    @http.route('/signup/pending', type='http', auth='public', website=True, sitemap=False)
    def exocoms_signup_pending(self, **kw):
        return request.render('exocoms_portal_signup.signup_pending', {
            'login': (kw.get('login') or '').strip(),
        })

    @http.route('/signup/activate/<string:token>', type='http', auth='public',
                website=True, sitemap=False)
    def exocoms_signup_activate(self, token, **kw):
        state, user = request.env['res.users'].sudo()._exocoms_activate_from_token(token)
        login = user.login if user else ''
        return request.render('exocoms_portal_signup.signup_activation_result', {
            'state': state,
            'login': login,
            'login_url': '/web/login?%s' % urlencode({'login': login}) if login else '/web/login',
        })

    @http.route('/signup/resend', type='http', auth='public', website=True,
                methods=['POST'], sitemap=False)
    def exocoms_signup_resend(self, **kw):
        login = (kw.get('login') or '').strip().lower()
        Users = request.env['res.users'].sudo()
        user = Users._exocoms_find_pending(login)
        error = ''
        if user:
            try:
                # Contrôle avant régénération : un renvoi refusé ne doit pas
                # invalider le lien déjà en circulation.
                user._exocoms_check_resend_allowed()
                user._exocoms_prepare_activation(
                    base_url=self._exocoms_request_base_url())
                user._exocoms_send_activation_email()
            except UserError as exc:
                error = exc.args[0]
        return request.render('exocoms_portal_signup.signup_pending', {
            'login': login,
            'error': error,
            'resent': not error,
        })

    # ==================================================================
    # Connexion sur un compte non activé
    # ==================================================================
    @http.route()
    def web_login(self, redirect=None, **kw):
        response = super().web_login(redirect=redirect, **kw)
        if request.httprequest.method != 'POST' or request.session.uid:
            return response
        if not request.env['res.users'].sudo()._exocoms_get_bool_param(
                'reveal_pending', True):
            return response
        login = (request.params.get('login') or '').strip().lower()
        if login and request.env['res.users'].sudo()._exocoms_find_pending(login):
            return request.redirect('/signup/pending?%s' % urlencode({
                'login': login, 'blocked': 1,
            }))
        return response
