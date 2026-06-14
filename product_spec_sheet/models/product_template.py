from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    spec_line_ids = fields.One2many(
        'product.template.spec.line', 'product_tmpl_id',
        string="Caractéristiques",
    )

    def _get_spec_categories(self):
        """Catégories utilisées par ce produit, triées pour l'affichage."""
        self.ensure_one()
        return self.spec_line_ids.category_id.sorted(key=lambda c: (c.sequence, c.name or ''))

    def _get_spec_lines_by_category(self, category):
        """Lignes de caractéristiques d'une catégorie donnée, triées."""
        self.ensure_one()
        return self.spec_line_ids.filtered(
            lambda line: line.category_id == category
        ).sorted(key=lambda line: (line.sequence, line.attribute_id.name or ''))

    def _get_spec_value(self, attribute):
        """Valeur de ce produit pour une caractéristique donnée, ou False si absente."""
        self.ensure_one()
        line = self.spec_line_ids.filtered(lambda l: l.attribute_id == attribute)
        return line.value if line else False
