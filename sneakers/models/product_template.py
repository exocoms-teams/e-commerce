from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        "product.brand",
        string="Brand",
    )

    old_price = fields.Float(
        string="Old Price",
    )

    badge = fields.Selection(
        [
            ("NEW", "NEW"),
            ("HOT", "HOT"),
            ("SALE", "SALE"),
        ],
        string="Badge",
    )