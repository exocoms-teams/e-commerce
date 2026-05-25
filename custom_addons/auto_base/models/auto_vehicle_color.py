from odoo import fields, models


class AutoVehicleColor(models.Model):
    _name = "auto.vehicle.color"
    _description = "Vehicle Color"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    hex_code = fields.Char(default="#FFFFFF")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "auto_vehicle_color_name_uniq",
            "unique(name)",
            "Color name must be unique.",
        )
    ]
