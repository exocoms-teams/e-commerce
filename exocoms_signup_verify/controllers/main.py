# -*- coding: utf-8 -*-
import logging

import werkzeug

from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import email_normalize

# On importe le contrôleur du module d'Eric pour l'étendre
from odoo.addons.exocoms_signup_activation.controllers.main import AuthSignupHome
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
    """Impose la validation de l'adresse email avant activation du compte en héritant d'Eric."""

    @http.route()
    def web_auth_signup(self, *args, **kw):
        # On conserve la logique de sécurité et de rendu existante
        return super().web_auth_signup(*args, **kw)

    def _exocoms_validate_signup_email(self, login):
        """
        Hook fourni par Eric dans exocoms_signup_activation.
        On y injecte toute notre logique de sécurité (Liste noire et MX).
        """
        # Toujours appeler le parent par bonne pratique
        super(ExocomsAuthSignupHome, self)._exocoms_validate_signup_email(login)

        # 1. Normalisation de l'email
        email = email_normalize(login)
        if not email:
            raise UserError(_("Cette adresse email n'est pas valide."))

        get_param = request.env["ir.config_parameter"].sudo().get_param
        domain = email.rsplit("@", 1)[-1]

        # 2. Vérification de la liste noire
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

        # 3. Vérification MX (email-validator)
        check_mx = get_param("exocoms_signup_verify.check_mx", "True") == "True"
        if check_mx and email_validator:
            try:
                email_validator.validate_email(email, check_deliverability=True)
            except email_validator.EmailNotValidError as err:
                raise UserError(
                    _("Le domaine de cette adresse email est introuvable "
                      "ou ne reçoit pas d'email.")
                ) from err

        return True