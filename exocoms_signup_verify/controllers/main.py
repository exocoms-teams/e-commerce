# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlencode

import werkzeug

from odoo import _, http
from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import email_normalize

# On importe le contrôleur du module d'Eric pour l'étendre
from odoo.addons.exocoms_signup_activation.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)

try:
    import email_validator
except ImportError:
    email_validator = None
    _logger.info(
        "exocoms_signup_verify : librairie 'email_validator' absente, "
        "le contrôle du domaine (MX) est désactivé."
    )


class ExocomsAuthSignupHomeVerify(AuthSignupHome):
    """Surcharge le contrôleur d'Eric pour injecter nos contrôles de sécurité (MX & Blacklist)."""

    def _exocoms_validate_signup_email(self, login):
        """Hook de validation de l'adresse email avant la création du compte.

        Lève une UserError dont le message sera proprement affiché sur le formulaire.
        """
        # 1. Appel du comportement parent (si nécessaire)
        super(ExocomsAuthSignupHomeVerify, self)._exocoms_validate_signup_email(login)

        # 2. Normalisation de l'email
        email = email_normalize(login)
        if not email:
            raise UserError(_("Cette adresse email n'est pas valide."))

        get_param = request.env["ir.config_parameter"].sudo().get_param
        domain = email.rsplit("@", 1)[-1]

        # 3. Contrôle de la liste noire (domaines jetables)
        blocked_domains_str = get_param("exocoms_signup_verify.blocked_domains", "")
        if blocked_domains_str:
            blocked_domains = [d.strip().lower() for d in blocked_domains_str.split(",") if d.strip()]
            if domain in blocked_domains:
                raise UserError(
                    _("Les adresses email jetables ne sont pas acceptées. "
                      "Merci d'utiliser une adresse valide.")
                )

        # 4. Contrôle MX (email-validator)
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