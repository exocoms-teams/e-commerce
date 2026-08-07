# -*- coding: utf-8 -*-
import logging
import werkzeug
from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import email_normalize
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)

try:
    import email_validator
except ImportError:  # pragma: no cover
    email_validator = None
    _logger.info(
        "exocoms_signup_verify : librairie 'email_validator' absente, "
        "le contrôle du domaine (MX) est désactivé."
    )

class ExocomsAuthSignupHome(AuthSignupHome):
    """Impose la validation de l'adresse email avant activation du compte."""

    @http.route()
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        # Inscription sur invitation (jeton) ou simple affichage du formulaire :
        # on conserve strictement le comportement natif.
        if qcontext.get("token") or request.httprequest.method != "POST":
            return super().web_auth_signup(*args, **kw)

        if not qcontext.get("signup_enabled"):
            raise werkzeug.exceptions.NotFound()

        try:
            login = self._exocoms_signup_pending(qcontext)
        except UserError as err:
            qcontext["error"] = err.args[0]
        except SignupError as err:
            _logger.warning("exocoms_signup_verify : inscription refusée (%s)", err)
            qcontext["error"] = _(
                "La création du compte a échoué. Merci de réessayer."
            )
        else:
            return request.render(
                "exocoms_signup_verify.signup_email_sent", {"login": login}
            )

        response = request.render("auth_signup.signup", qcontext)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _exocoms_signup_pending(self, qcontext):
        """Crée le compte sans mot de passe et envoie le lien d'activation.
        Retourne l'adresse email normalisée. N'authentifie jamais le visiteur.
        """
        name = (qcontext.get("name") or "").strip()
        if not name:
            raise UserError(_("Merci de renseigner votre nom."))
            
        login = self._exocoms_validate_email(qcontext.get("login") or "")
        Users = request.env["res.users"].sudo()
        
        existing = Users.with_context(active_test=False).search(
            Users._get_login_domain(login), order=Users._get_login_order(), limit=1
        )
        
        if not existing:
            existing = Users.with_context(active_test=False).search(
                Users._get_email_domain(login), limit=1
            )
            
        if existing:
            # Aucune énumération de comptes : on affiche le même écran dans tous
            # les cas. Un compte jamais activé reçoit simplement un nouveau lien.
            if existing.active and existing.state == "new":
                existing.with_context(create_user=1).action_reset_password()
                request.env.cr.commit()
            return login
            
        values = {"login": login, "email": login, "name": name}
        lang = request.env.context.get("lang", "")
        if lang in [code for code, _label in request.env["res.lang"].get_installed()]:
            values["lang"] = lang
            
        try:
            # Pas de clé 'password' : l'utilisateur est créé à l'état "new",
            # sans mot de passe, donc inutilisable tant que le lien n'est pas consommé.
            Users.signup(values)
            user = Users.search(
                Users._get_login_domain(login), order=Users._get_login_order(), limit=1
            )
            # create_user=1 => signup_type "signup" => mail auth_signup.portal_set_password_email
            user.with_context(create_user=1).action_reset_password()
        except UserError:
            # Envoi du mail impossible : on annule la création pour que le
            # visiteur puisse réessayer avec un compte propre.
            request.env.cr.rollback()
            raise
            
        request.env.cr.commit()
        _logger.info(
            "exocoms_signup_verify : compte en attente de validation pour <%s>", login
        )
        return login

    def _exocoms_validate_email(self, login):
        """Normalise et contrôle l'adresse email fournie."""
        email = email_normalize(login)
        if not email:
            raise UserError(_("Cette adresse email n'est pas valide."))
            
        get_param = request.env["ir.config_parameter"].sudo().get_param
        domain = email.rsplit("@", 1)[-1]
        
        blocked = [
            d.strip().lower()
            for d in (get_param("exocoms_signup_verify.blocked_domains") or "").split(",")
            if d.strip()
        ]
        
        if domain in blocked:
            raise UserError(
                _("Les adresses email jetables ne sont pas acceptées. "
                  "Merci d'utiliser une adresse professionnelle.")
            )
            
        check_mx = get_param("exocoms_signup_verify.check_mx", "True") == "True"
        if check_mx and email_validator:
            try:
                email_validator.validate_email(email, check_deliverability=True)
            except email_validator.EmailNotValidError as err:
                raise UserError(
                    _("Le domaine de cette adresse email est introuvable "
                      "ou ne reçoit pas d'email.")
                ) from err
                
        return email