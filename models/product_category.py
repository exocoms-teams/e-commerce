from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    # Pour classer les catégories par ordre de préférences (côté UI)
    sequence = fields.Integer(default=10, index=True)
    _order = "sequence, name"

    tire_category = fields.Char()
