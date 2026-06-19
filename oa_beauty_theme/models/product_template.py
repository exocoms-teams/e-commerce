from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    oa_type = fields.Char(
        string='Beauty Product Type',
        help='e.g. "Lip Colour", "Brightening Serum", "Liquid Foundation" — '
             'migrated from the type field in the original LUMIÈRE data.js',
    )
    oa_finish = fields.Char(
        string='Finish',
        help='e.g. "Matte Velvet", "Natural Satin", "Mixed — Matte & Shimmer" — '
             'migrated from the finish field in the original LUMIÈRE data.js',
    )
    oa_best_for = fields.Char(
        string='Best For',
        help='e.g. "Long-lasting wear", "Dull & uneven skin" — '
             'migrated from the bestFor field in the original LUMIÈRE data.js',
    )
    oa_key_ingredients = fields.Char(
        string='Key Ingredients',
        help='Comma-separated list, e.g. "Shea Butter, Vitamin E, Jojoba Oil" — '
             'migrated from the keyIngredients field in the original LUMIÈRE data.js',
    )
