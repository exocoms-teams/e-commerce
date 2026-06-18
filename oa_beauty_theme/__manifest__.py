# -*- coding: utf-8 -*-
{
    'name': "O&A Beauty - Clean Luxury Cosmetics Theme",
    'version': '19.0.1.3.0',
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
        # NB: no separate wishlist module dependency. Its exact technical
        # name is inconsistent even across Odoo's own official 19.0
        # documentation (one official manifest example uses
        # "website_sale_wishlist", a comment elsewhere in the same repo
        # references "website_sale_whishlist") and neither was confirmed
        # available on this project's live Odoo.sh instance. It is not
        # required: per Odoo 19.0's own "Additional features" docs, the
        # wishlist heart button is already enabled by default on the
        # product page as soon as website_sale is installed — no extra
        # dependency needed. If you later want a *persistent* (saved
        # across sessions) wishlist and your instance does offer a
        # dedicated module for it, check Apps (search "wishlist") on
        # your live database to find its exact current name, then add
        # it here.
    ],
    'data': [
        'data/product_attribute_data.xml',
        'data/product_public_category_data.xml',
        'views/product_template_backend_views.xml',
        'views/website_sale_product_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'oa_beauty_theme/static/src/scss/components.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
