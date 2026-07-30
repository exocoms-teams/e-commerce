from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand = fields.Selection([
        ('nike', 'Nike'),
        ('adidas', 'Adidas'),
        ('puma', 'Puma'),
        ('new_balance', 'New Balance'),
        ('converse', 'Converse'),
    ], string='Brand')
    color = fields.Selection([
        ('black', 'Black'),
        ('white', 'White'),
        ('orange', 'Orange'),
        ('blue', 'Blue'),
        ('red', 'Red'),
        ('green', 'Green'),
    ], string='Color')
    size = fields.Selection([
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
    ], string='Size')
    in_stock = fields.Boolean(string='In Stock', default=True)
