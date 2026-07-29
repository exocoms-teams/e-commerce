from odoo import models, fields, api


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

    # Stock display control (admin toggle)
    website_availability = fields.Selection([
        ('always', 'Always Available'),
        ('threshold', 'Show Based on Stock'),
        ('never', 'Never Show Stock'),
    ], string="Stock Display", default='always',
        help="Control how stock is shown on the website. "
             "'Always Available' hides stock info. "
             "'Show Based on Stock' shows quantity and out-of-stock state. "
             "'Never Show Stock' hides stock but allows ordering.")

    allow_out_of_stock_order = fields.Boolean(
        string="Allow Out-of-Stock Orders",
        default=True,
        help="If checked, customers can order even when product is out of stock."
    )

    stock_threshold = fields.Integer(
        string="Low Stock Threshold",
        default=5,
        help="Show 'Low Stock' warning when quantity is below this number."
    )