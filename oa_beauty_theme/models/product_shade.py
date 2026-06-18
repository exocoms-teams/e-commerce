# -*- coding: utf-8 -*-
from odoo import models, fields

class LumiereProductShade(models.Model):
    _name = 'lumiere.product.shade'
    _description = 'Teintes de Produits LUMIÈRE'

    name = fields.Char(string="Nom de la Teinte", required=True) # Ex: Rose Petal
    color_code = fields.Char(string="Code Couleur (Hex)", required=True) # Ex: #c17e8a
    product_tmpl_id = fields.Many2one('product.template', string="Produit Associé", ondelete='cascade')