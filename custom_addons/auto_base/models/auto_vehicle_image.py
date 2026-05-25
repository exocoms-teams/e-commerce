from odoo import fields, models


class AutoVehicleImage(models.Model):
    _name = "auto.vehicle.image"
    _description = "Vehicle Gallery Image"
    _order = "sequence, id"

    vehicle_id = fields.Many2one("auto.vehicle", required=True, ondelete="cascade")
    name = fields.Char(required=True, translate=True)
    image_1920 = fields.Image(required=True, max_width=1920, max_height=1920)
    sequence = fields.Integer(default=10)
    is_cover = fields.Boolean(default=False)
    alt_text = fields.Char(translate=True)
