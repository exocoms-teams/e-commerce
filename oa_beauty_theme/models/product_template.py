# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    """Adds the four cosmetics-specific spec fields that the static site
    hard-coded per product in data.js (type, finish, bestFor,
    keyIngredients). Everything else from data.js maps onto stock Odoo
    fields:

        data.js field   -> Odoo field
        ----------------------------------------------------------------
        name             -> name
        category          -> public_categ_ids (product.public.category)
        price             -> list_price
        img               -> image_1920 / product.image (gallery)
        description       -> description_sale (shown on the shop page)
        shades[]          -> product.template.attribute.line on the
                              "Shade" attribute (display_type='color')
        rating / reviews  -> native website_sale "Comments & Ratings"
                              (rating.mixin), NOT migrated as static
                              numbers — see blueprint risk section.
        icon / shade hex  -> dropped (was a placeholder for missing
                              product photography; replace with real
                              product photos in image_1920 / extra images)
    """
    _inherit = 'product.template'

    oa_type = fields.Char(
        string="Type",
        help="Short product type label shown on the product page, "
             "e.g. 'Lip Colour', 'Brightening Serum'. Maps from data.js "
             "field 'type'.",
    )
    oa_finish = fields.Char(
        string="Finish",
        help="e.g. 'Matte Velvet', 'Natural Satin'. Maps from data.js "
             "field 'finish'.",
    )
    oa_best_for = fields.Char(
        string="Best For",
        help="e.g. 'Long-lasting wear'. Maps from data.js field 'bestFor'.",
    )
    oa_key_ingredients = fields.Char(
        string="Key Ingredients",
        help="Comma-separated ingredient highlight line, e.g. "
             "'Shea Butter, Vitamin E, Jojoba Oil'. Maps from data.js "
             "field 'keyIngredients'. Kept as a single display line to "
             "match the original .ing-value layout; use the standard "
             "'Ingredients' / allergen fields instead if you need "
             "structured, regulation-grade INCI data later.",
    )
