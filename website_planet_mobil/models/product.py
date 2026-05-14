from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_new = fields.Boolean(
        string='Nouveau produit',
        default=False,
    )
    is_best_seller = fields.Boolean(
        string='Best Seller',
        default=False,
    )