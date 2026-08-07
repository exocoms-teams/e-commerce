# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    exocoms_signup_check_mx = fields.Boolean(
        string="Vérifier le domaine de l'email",
        config_parameter="exocoms_signup_verify.check_mx",
        default=True,
        help="Contrôle l'existence d'un enregistrement MX pour le domaine saisi.\n"
             "Nécessite la librairie Python 'email_validator' ; sans elle, "
             "l'option est sans effet.",
    )
    exocoms_signup_blocked_domains = fields.Char(
        string="Domaines email refusés",
        config_parameter="exocoms_signup_verify.blocked_domains",
        help="Liste séparée par des virgules, par exemple : "
             "yopmail.com,mailinator.com,10minutemail.com",
    )