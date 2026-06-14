from odoo import fields, models


class ProductSpecAttribute(models.Model):
    """Caractéristique réutilisable, classée dans une catégorie (ex: Batterie, Encombrement)."""

    _name = 'product.spec.attribute'
    _description = "Caractéristique produit"
    _order = 'category_id, sequence, name'

    name = fields.Char(string="Caractéristique", required=True, translate=True)
    category_id = fields.Many2one(
        'product.spec.category', string="Catégorie",
        required=True, ondelete='restrict',
    )
    sequence = fields.Integer(string="Séquence", default=10)
