from odoo import models, fields


class TireUsage(models.Model):
    """Contexte d'utilisation d'un pneu (marketing)"""

    _name = "tire.usage"
    _description = "Usage du pneu"
    _order = "sequence, name"

    name = fields.Char(required=True)
    usage = fields.Char(required=True, index=True)

    sequence = fields.Integer(default=10)

    # active = fields.Boolean(default=True)
