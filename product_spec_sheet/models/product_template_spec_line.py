from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplateSpecLine(models.Model):
    """Valeur d'une caractéristique pour un produit donné."""

    _name = 'product.template.spec.line'
    _description = "Ligne de caractéristique produit"
    _order = 'category_id, sequence, id'

    product_tmpl_id = fields.Many2one(
        'product.template', string="Produit",
        required=True, ondelete='cascade',
    )
    attribute_id = fields.Many2one(
        'product.spec.attribute', string="Caractéristique",
        required=True, ondelete='restrict',
    )
    category_id = fields.Many2one(
        related='attribute_id.category_id', store=True, readonly=True,
        string="Catégorie",
    )
    sequence = fields.Integer(related='attribute_id.sequence', store=True, readonly=True)
    value = fields.Char(string="Valeur", required=True, translate=True)

    @api.constrains('product_tmpl_id', 'attribute_id')
    def _check_unique_attribute_per_product(self):
        for rec in self:
            duplicate = self.search([
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
                ('attribute_id', '=', rec.attribute_id.id),
                ('id', '!=', rec.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    "Cette caractéristique est déjà renseignée pour ce produit."
                )
