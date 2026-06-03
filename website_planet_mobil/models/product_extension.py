# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_is_top_vente = fields.Boolean(string='Top Vente', default=False)
    x_is_nouveaute = fields.Boolean(string='Nouveauté', default=False)
    x_is_promotion = fields.Boolean(
        string='Promotion',
        compute='_compute_is_promotion',
        store=True
    )  
    x_brand = fields.Char(string='Marque')
    x_specs = fields.Text(string='Caractéristiques')

    @api.depends('pricelist_rule_ids')
    def _compute_is_promotion(self):
        for product in self:
            product.x_is_promotion = bool(product.pricelist_rule_ids)