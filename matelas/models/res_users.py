# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    """Ajoute les informations utilisées pour la confirmation d'email."""
    _inherit = 'res.users'

    matelas_email_confirm_token = fields.Char(
        string="Jeton de confirmation d'email",
        copy=False,
    )

    matelas_email_confirm_expiry = fields.Datetime(
        string="Expiration du jeton de confirmation",
        copy=False,
    )
