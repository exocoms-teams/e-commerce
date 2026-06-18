# -*- coding: utf-8 -*-
{
    'name': "O&A Beauty — LUMIÈRE Theme",
    'version': '19.0.2.0.0',
    'category': 'Website/Website',
    'summary': "Full LUMIÈRE frontend migration: custom homepage, shop, product page & SCSS",
    'description': """
O&A Beauty — LUMIÈRE Complete Theme (v2)
=========================================
Full migration of the original LUMIÈRE static HTML/CSS frontend into Odoo 19.

What this module delivers:
--------------------------
1. **Custom Homepage** ("/") via a QWeb template + Python controller:
   - Hero section (gradient bg, title, CTAs)
   - Marquee trust-bar
   - About section with statistics
   - Shop preview grid (live published products)
   - Gallery mosaic
   - Features / USP strip
   - Testimonials
   - Contact section (links to /contactus)
   - Newsletter bar

2. **Complete LUMIÈRE SCSS** (lumiere_theme.scss):
   - CSS custom properties (brand tokens: mauve, lilac, ivory, prune)
   - Cormorant Garamond + Jost fonts
   - All homepage sections styled
   - /shop page override (product cards, category pills, sidebar)
   - /shop/product detail page (accordion, swatches, add-to-cart button)
   - Cart/checkout button overrides
   - Footer override
   - Full responsive (tablet + mobile)

3. **Product detail accordion** (website_sale_product_templates.xml):
   - Product Details (Type / Finish / Best For / Key Ingredients)
   - Delivery & Returns trust badges

4. **Custom product fields** (models/product_template.py):
   - oa_type, oa_finish, oa_best_for, oa_key_ingredients

5. **Data** (product_attribute_data.xml, product_public_category_data.xml)
""",
    'author': "O&A Beauty / Migration Project",
    'website': "https://www.oabeauty.example",
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
    ],
    'data': [
        'data/product_attribute_data.xml',
        'data/product_public_category_data.xml',
        'views/product_template_backend_views.xml',
        'views/website_homepage.xml',
        'views/website_sale_product_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # Main theme first (tokens + layout), then component overrides
            'oa_beauty_theme/static/src/scss/lumiere_theme.scss',
            'oa_beauty_theme/static/src/scss/components.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
