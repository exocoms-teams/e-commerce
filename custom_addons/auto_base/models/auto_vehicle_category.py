from odoo import fields, models


class AutoVehicleCategory(models.Model):
    _name = "auto.vehicle.category"
    _description = "Catégorie de véhicule"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text(translate=True)
    icon = fields.Image(max_width=512, max_height=512)

    if hasattr(models, "Constraint"):
        _name_uniq = models.Constraint(
            "unique(name)",
            "Le nom de la catégorie doit être unique.",
        )
    else:
        _sql_constraints = [
            (
                "auto_vehicle_category_name_uniq",
                "unique(name)",
                "Le nom de la catégorie doit être unique.",
            )
        ]
