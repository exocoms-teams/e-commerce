# -*- coding: utf-8 -*-
{
    'name': "O&A Beauty - Clean Luxury Cosmetics Theme",
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': "Theme + product-page extensions migrated from the LUMIÈRE static frontend",
    'description': """
O&A Beauty Website Theme
=========================
Custom module supporting the migration of the LUMIÈRE static HTML/CSS/JS
e-commerce frontend into Odoo 19 Website + eCommerce.

What this module does (and ONLY this — everything else is native Odoo,
configured through the Website Builder, no code required):

* Brand SCSS tokens (mauve / lilac / ivory / prune) layered on top of the
  Odoo website asset bundles.
* Four extra product.template fields (Type, Finish, Best For, Key
  Ingredients) that the static site hard-coded into product.js.
* A QWeb extension of the native eCommerce product page that renders those
  four fields plus the trust-badge row (free delivery / returns /
  cruelty-free), matching the original .detail-specs / .detail-ingredients
  / .detail-meta blocks.

Cart, checkout, variant/shade selection, related products, mobile menu,
star-rating display and the contact form are all handled by stock Odoo
(website_sale, website, mail) and are intentionally NOT re-implemented
here. See the migration blueprint document for the full mapping.
""",
    'author': "O&A Beauty / Migration Project",
    'website': "https://www.oabeauty.example",
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
        'website_sale_wishlist',  # replaces the decorative localStorage wishlist heart
    ],
    'data': [
        'data/product_attribute_data.xml',
        'data/product_public_category_data.xml',
        'views/product_template_backend_views.xml',
        'views/website_sale_product_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'oa_beauty_theme/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
            'oa_beauty_theme/static/src/scss/components.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
