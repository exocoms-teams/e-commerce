from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    oa_type = fields.Char(string='Cosmetic Type')
    oa_finish = fields.Char(string='Finish')
    oa_best_for = fields.Char(string='Best For')
    oa_key_ingredients = fields.Char(string='Key Ingredients')
