from odoo import fields, models


class AutoSpecification(models.Model):
    _name = "auto.specification"
    _description = "Vehicle Specification"
    _order = "sequence, id"

    SECTION_SELECTION = [
        ("performance", "Performance"),
        ("dimensions", "Dimensions"),
        ("energy", "Energy"),
        ("safety", "Safety"),
        ("comfort", "Comfort"),
        ("other", "Other"),
    ]

    vehicle_id = fields.Many2one("auto.vehicle", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    section = fields.Selection(SECTION_SELECTION, default="other", required=True)
    name = fields.Char(required=True, translate=True)
    value = fields.Char(required=True, translate=True)
    unit = fields.Char(translate=True)
