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

    # ==================================================================
    # Inscription
    # ==================================================================
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            # Invitation émise depuis le back-office : l'adresse est déjà
            # connue de l'entreprise, on conserve le comportement natif Odoo.
            if qcontext.get('token'):
                return super().web_auth_signup(*args, **kw)

            try:
                user_sudo = self._exocoms_signup_pending(qcontext)
                return request.redirect('/signup/pending?%s' % urlencode({
                    'login': user_sudo.login,
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
                    _logger.warning("Échec de création du compte portail : %s", error)
                    qcontext['error'] = _("Impossible de créer le compte.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    def _exocoms_signup_pending(self, qcontext):
        """Crée le compte en attente de validation et envoie l'email."""
        Users = request.env['res.users'].sudo()

        def _get(key):
            # get_auth_signup_qcontext() filtre les paramètres via
            # SIGN_UP_REQUEST_PARAMS ; on retombe sur request.params pour rester
            # tolérant si le formulaire du thème poste des champs différents.
            value = qcontext.get(key) or request.params.get(key) or ''
            return value.strip() if isinstance(value, str) else value

        login = _get('login') or _get('email')
        password = _get('password')
        # Odoo natif ne rend pas le nom obligatoire : signup() le dérive de
        # l'adresse email lorsqu'il est absent. On garde ce comportement.
        name = _get('name') or login

        if not login or not password:
            _logger.warning(
                "Inscription refusée : champs manquants. Champs reçus = %s",
                sorted(request.params.keys()))
            raise UserError(_(
                "Merci de renseigner votre adresse email et un mot de passe."))
        # La confirmation n'est comparée que si le formulaire la transmet
        # réellement : certains thèmes n'affichent pas ce second champ.
        confirm = _get('confirm_password')
        if confirm and password != confirm:
            raise UserError(_("Les mots de passe ne correspondent pas ; "
                              "merci de les saisir à nouveau."))

        values = {'login': login, 'name': name, 'password': password}

        # Point d'extension : contrôles supplémentaires sur l'adresse email
        # (format, enregistrement MX, domaines jetables...). Surchargez cette
        # méthode — ou branchez-y exocoms_signup_verify — pour refuser une
        # inscription avant même la création du compte.
        self._exocoms_validate_signup_email(login)

        supported_lang_codes = [code for code, _label in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang

        # Inscription déjà déposée mais jamais activée : on régénère un jeton
        # et on relance l'email plutôt que de renvoyer une erreur.
        pending = Users._exocoms_find_pending(login)
        if pending:
            # Le mot de passe et le nom soumis sont volontairement ignorés : un
            # tiers qui connaît l'adresse ne doit pas pouvoir écraser les
            # identifiants d'une inscription en cours. On se contente de
            # relancer l'email — soumis aux mêmes limites que le bouton de
            # renvoi, sans quoi le formulaire deviendrait un outil de mail bomb.
            try:
                pending._exocoms_check_resend_allowed()
                pending._exocoms_prepare_activation(
                    base_url=self._exocoms_request_base_url())
                pending._exocoms_send_activation_email(silent=True)
            except UserError:
                _logger.info(
                    "Ré-inscription ignorée (limite d'envoi atteinte) : %s", login)
            return pending

        created_login, _password = Users.signup(values, None)
        user_sudo = Users.with_context(active_test=False).search(
            Users._get_login_domain(created_login),
            order=Users._get_login_order(), limit=1)
        if not user_sudo:
            raise SignupError(_("Impossible de créer le compte."))

        user_sudo._exocoms_prepare_activation(
            base_url=self._exocoms_request_base_url())
        # On sécurise la création du compte avant l'envoi du mail : si le
        # serveur SMTP échoue, l'inscription n'est pas perdue et le visiteur
        # peut demander un nouvel envoi.
        request.env.cr.commit()
        try:
            user_sudo._exocoms_send_activation_email(silent=True)
        except Exception:  # noqa: BLE001 - SMTP indisponible, quota, etc.
            _logger.exception(
                "Envoi de l'email d'activation impossible pour %s", login)
        return user_sudo

    def _exocoms_request_base_url(self):
        """Racine d'URL du site sur lequel la demande a ete deposee.

        En multi-societe / multi-site, garantit que le client recoit un lien
        pointant vers le domaine par lequel il s'est inscrit, et non vers le
        `web.base.url` global de la base.
        """
        website = getattr(request, 'website', None)
        if website and website.domain:
            domain = website.domain.strip()
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://%s' % domain
            return domain
        return request.httprequest.url_root

    def _exocoms_validate_signup_email(self, login):
        """Hook de validation de l'adresse email avant création du compte.

        Ne fait rien par défaut. Doit lever une ``UserError`` (dont le message
        sera affiché sur le formulaire d'inscription) si l'adresse doit être
        refusée.
        """
        return True

    # ==================================================================
    # Connexion : compte non activé
    # ==================================================================
    @http.route()
    def web_login(self, redirect=None, **kw):
        response = super().web_login(redirect=redirect, **kw)

        if request.httprequest.method != 'POST' or request.session.uid:
            return response

        reveal = request.env['ir.config_parameter'].sudo().get_param(
            'exocoms_signup_activation.reveal_pending', 'True')
        if reveal in ('False', 'false', '0', ''):
            return response

        login = request.params.get('login')
        user = request.env['res.users'].sudo()._exocoms_find_pending(login)
        if not user:
            return response

        return request.redirect('/signup/pending?%s' % urlencode({
            'login': user.login,
            'notice': 'not_activated',
        }))

    # ==================================================================
    # Pages publiques d'activation
    # ==================================================================
    @http.route('/signup/pending', type='http', auth='public', website=True, sitemap=False)
    def exocoms_signup_pending(self, login=None, notice=None, resent=None, error=None, **kw):
        return request.render('exocoms_signup_activation.signup_pending', {
            'login': login or '',
            'notice': notice or '',
            'resent': resent == '1',
            'error': error or '',
        })

    @http.route('/signup/activate/<string:token>', type='http', auth='public',
                website=True, sitemap=False)
    def exocoms_signup_activate(self, token, **kw):
        user, state = request.env['res.users'].sudo()._exocoms_activate_from_token(token)

        if state in ('ok', 'already'):
            return request.render('exocoms_signup_activation.signup_activated', {
                'login': user.login,
                'already': state == 'already',
                'login_url': '/web/login?%s' % urlencode({
                    'login': user.login,
                    'redirect': '/my',
                }),
            })

        return request.render('exocoms_signup_activation.signup_activation_failed', {
            'state': state,
            'login': user.login if user else '',
        })

    @http.route('/signup/resend', type='http', auth='public', methods=['POST'],
                website=True, sitemap=False)
    def exocoms_signup_resend(self, login=None, **kw):
        error = ''
        user = request.env['res.users'].sudo()._exocoms_find_pending(login)
        if user:
            try:
                # Contrôle AVANT régénération : un renvoi refusé ne doit pas
                # invalider le lien déjà reçu par le client.
                user._exocoms_check_resend_allowed()
                user._exocoms_prepare_activation(
                    base_url=self._exocoms_request_base_url())
                user._exocoms_send_activation_email(silent=True)
            except UserError as exc:
                error = exc.args[0]

        # On redirige systématiquement vers la même page, que le compte existe
        # ou non, afin de ne pas divulguer l'existence d'une adresse email.
        params = {'login': login or '', 'resent': '1'}
        if error:
            params['error'] = error
        return request.redirect('/signup/pending?%s' % urlencode(params))
