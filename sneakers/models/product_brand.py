from odoo import models, fields


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _order = "name"

    name = fields.Char(
        string="Brand Name",
        required=True,
    )

    logo = fields.Image(
        string="Brand Logo",
    )