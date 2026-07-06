# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Marque produit"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    logo = fields.Image(string="Logo", max_width=256, max_height=256)
    color = fields.Char(
        string="Couleur d'accent",
        help="Couleur hexadécimale de la pastille (ex: #d6002a).",
    )
    product_count = fields.Integer(
        string="Nb produits", compute="_compute_product_count"
    )

    def _compute_product_count(self):
        Product = self.env["product.template"]
        for brand in self:
            brand.product_count = Product.search_count(
                [("brand_id", "=", brand.id)]
            )

    @api.model
    def exocoms_get_brands(self, website_id=None):
        """Liste des marques présentes parmi les produits publiés du site,
        avec nombre de produits et quantité disponible agrégée."""
        website = self.env["website"].browse(website_id) \
            if website_id else self.env["website"].get_current_website()
        Product = self.env["product.template"].sudo()
        products = Product.search([
            ("is_published", "=", True),
            ("website_id", "in", [False, website.id]),
            ("brand_id", "!=", False),
        ])
        data = {}
        for product in products:
            brand = product.brand_id
            entry = data.setdefault(brand.id, {
                "id": brand.id,
                "name": brand.name,
                "color": brand.color or "",
                "product_count": 0,
                "qty_available": 0,
            })
            entry["product_count"] += 1
            entry["qty_available"] += int(product.qty_available)
        return sorted(data.values(), key=lambda b: b["name"])


class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        "product.brand", string="Marque", index=True,
        help="Marque du produit, utilisée par le filtre de la boutique.",
    )
