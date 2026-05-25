from odoo import fields, models


class AutoMotorization(models.Model):
    _name = "auto.motorization"
    _description = "Vehicle Motorization"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(index=True)
    description = fields.Text(translate=True)
    is_electrified = fields.Boolean(default=False)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "auto_motorization_name_uniq",
            "unique(name)",
            "Motorization name must be unique.",
        ),
    ]
