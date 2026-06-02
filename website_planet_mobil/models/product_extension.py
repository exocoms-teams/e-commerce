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

    @api.depends('item_ids', 'list_price')
    def _compute_is_promotion(self):
        for product in self:
            product.x_is_promotion = bool(
                product.item_ids.filtered(
                    lambda i: (
                        i.compute_price == 'discount' and i.price_discount > 0
                    ) or (
                        i.compute_price == 'formula' and (i.price_discount > 0 or i.price_extra < 0)
                    ) or (
                        i.compute_price == 'fixed' and i.fixed_price < product.list_price
                    )
                )
            )