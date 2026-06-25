from odoo import models, fields


class TireTreadPattern(models.Model):
    """ "Profil de bande de roulement"""

    _name = "tire.tread.pattern"
    _description = "Profil de bande de roulement"

    name = fields.Char(required=True)
    pattern_category = fields.Char(
        required=True,
    )
