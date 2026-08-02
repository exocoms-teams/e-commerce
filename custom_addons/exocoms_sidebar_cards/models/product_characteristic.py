# -*- coding: utf-8 -*-
from odoo import fields, models


class ExocomsProductCharacteristic(models.Model):
    _name = "exocoms.product.characteristic"
    _description = "Caractéristique produit EXOCOMS"
    _order = "sequence, id"

    product_tmpl_id = fields.Many2one(
        "product.template", string="Produit",
        required=True, ondelete="cascade", index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Caractéristique", required=True, translate=True)
    value = fields.Char(string="Valeur", translate=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    characteristic_ids = fields.One2many(
        "exocoms.product.characteristic", "product_tmpl_id",
        string="Caractéristiques",
    )