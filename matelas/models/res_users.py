# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    """Ajoute le jeton utilisé pour la confirmation d'email obligatoire."""
    _inherit = 'res.users'

    matelas_email_confirm_token = fields.Char(copy=False)
