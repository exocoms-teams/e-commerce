from odoo import fields, models


class ProductSpecCategory(models.Model):
    """Regroupement de caractéristiques produit (ex: Connectivité, Écran, Alimentation)."""

    _name = 'product.spec.category'
    _description = "Catégorie de caractéristique produit"
    _order = 'sequence, name'

    name = fields.Char(string="Catégorie", required=True, translate=True)
    sequence = fields.Integer(string="Séquence", default=10)
    attribute_ids = fields.One2many(
        'product.spec.attribute', 'category_id', string="Caractéristiques",
    )
