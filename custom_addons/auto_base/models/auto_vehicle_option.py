from odoo import fields, models


class AutoVehicleOption(models.Model):
    _name = "auto.vehicle.option"
    _description = "Option du véhicule"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    option_type = fields.Selection(
        [
            ("safety", "Sécurité"),
            ("comfort", "Comfort"),
            ("multimedia", "Multimédia"),
            ("driving", "Aide à la conduite"),
            ("charging", "Recharge"),
            ("other", "Autre"),
        ],
        default="other",
        required=True,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text(translate=True)

    _sql_constraints = [
        (
            "auto_vehicle_option_name_uniq",
            "unique(name)",
            "Le nom de l'option doit être unique.",
        )
    ]
