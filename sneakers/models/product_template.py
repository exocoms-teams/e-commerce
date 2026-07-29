from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        "product.brand",
        string="Brand"
    )

    sku = fields.Char(
        string="SKU"
    )

    old_price = fields.Float(
        string="Old Price"
    )

    rating = fields.Float(
        string="Rating",
        default=5.0
    )

    review_count = fields.Integer(
        string="Review Count",
        default=0
    )

    material = fields.Char(
        string="Material"
    )

    sole = fields.Char(
        string="Sole"
    )

    weight = fields.Char(
        string="Weight"
    )

    origin = fields.Char(
        string="Country of Origin"
    )