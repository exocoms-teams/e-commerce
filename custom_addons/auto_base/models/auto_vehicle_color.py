from odoo import fields, models


class AutoVehicleColor(models.Model):
    _name = "auto.vehicle.color"
    _description = "Couleur de véhicule"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    hex_code = fields.Char(default="#FFFFFF")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    if hasattr(models, "Constraint"):
        _name_uniq = models.Constraint(
            "unique(name)",
            "Le nom de la couleur doit être unique.",
        )
    else:
        _sql_constraints = [
            (
                "auto_vehicle_color_name_uniq",
                "unique(name)",
                "Le nom de la couleur doit être unique.",
            )
        ]
