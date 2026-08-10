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

    # ══════════════════════════════════════════════════════════════
    # FILTRAGE SUR LE SITE E-COMMERCE
    # ══════════════════════════════════════════════════════════════

    website_filter = fields.Boolean(
        string="Filtrable sur le site",
        default=False,
        help="Affiche cette caractéristique comme filtre dans la boutique en ligne.",
    )
    filter_sequence = fields.Integer(
        string="Ordre du filtre", default=10,
    )

    def get_filter_values(self):
        """
        Renvoie les valeurs distinctes de cette caractéristique parmi les
        produits publiés, avec le nombre de produits pour chacune.
        Format : [{'value': '4G', 'count': 12}, ...]
        """
        self.ensure_one()
        lines = self.env["product.template.spec.line"].sudo().search([
            ("attribute_id", "=", self.id),
            ("product_tmpl_id.website_published", "=", True),
        ])
        counts = {}
        for line in lines:
            # Une valeur peut contenir plusieurs termes séparés par des virgules
            for token in (line.value or "").split(","):
                token = token.strip()
                if token:
                    counts[token] = counts.get(token, 0) + 1
        return [
            {"value": v, "count": c}
            for v, c in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        ][:15]
