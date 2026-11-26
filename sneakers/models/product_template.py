from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"


    # =====================
    # Sneakers specific data
    # =====================

    brand_id = fields.Many2one(
        "product.brand",
        string="Brand"
    )


    # =====================
    # Website stock control
    # =====================

    website_availability = fields.Selection([
        ('always', 'Always Available'),
        ('threshold', 'Show Based on Stock'),
        ('never', 'Never Show Stock'),
    ],
    string="Stock Display",
    default='always')


    allow_out_of_stock_order = fields.Boolean(
        string="Allow Out-of-Stock Orders",
        default=True
    )


    stock_threshold = fields.Integer(
        string="Low Stock Threshold",
        default=5
    )


    # =====================
    # Soukaina / PRD fields
    # =====================

    country_of_origin = fields.Many2one(
        "res.country",
        string="Country of Origin",
    )