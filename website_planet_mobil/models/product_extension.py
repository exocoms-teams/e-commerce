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
    x_product_categ_ids = fields.Many2many(
        'product.public.category',
        'product_attribute_public_category_rel',
        'attribute_id',
        'category_id',
        string='Catégories produits'
    )

    @api.depends('pricelist_rule_ids')
    def _compute_is_promotion(self):
        for product in self:
            product.x_is_promotion = bool(product.pricelist_rule_ids)

    def _search_get_detail(self, website, order, options):
        result = super()._search_get_detail(website, order, options)
        if options.get('x_is_promotion'):
            result['base_domain'].append([('x_is_promotion', '=', True)])
        return result