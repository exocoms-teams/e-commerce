from odoo import fields, models


class AutoVehicleOption(models.Model):
    _name = "auto.vehicle.option"
    _description = "Vehicle Option"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    option_type = fields.Selection(
        [
            ("safety", "Safety"),
            ("comfort", "Comfort"),
            ("multimedia", "Multimedia"),
            ("driving", "Driving Assistance"),
            ("charging", "Charging"),
            ("other", "Other"),
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
            "Option name must be unique.",
        )
    ]
