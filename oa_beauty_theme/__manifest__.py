{
    'name': 'O&A Beauty — Clean Luxury Cosmetics Theme',
    'version': '19.0.2.0.0',
    'category': 'Website/Theme',
    'summary': 'Complete LUMIÈRE frontend migrated to Odoo 19: homepage, shop, product page, brand SCSS',
    'description': """
        Full migration of the LUMIÈRE static cosmetics e-commerce frontend to Odoo 19.

        What this module delivers:
        - Custom branded homepage at / (Hero / About / Shop preview / Gallery / Contact)
        - LUMIÈRE design system (Cormorant Garamond + Jost, mauve-lilac-ivory-prune palette)
        - Shop page (/shop) restyled to match original product-card design
        - Product page with Type / Finish / Best For / Key Ingredients accordion section
        - Trust badges (delivery / returns / cruelty-free) in product accordion
        - Shade colour-attribute with CSS circles (native website_sale variant selection)
        - 4 public product categories: Lips / Face / Skincare / Eyes
        - Contact form with server-side mail delivery (no EmailJS key required)
        - Responsive layout (1285px / 1100px / 768px / 600px breakpoints from original)

        Dependencies: website, website_sale, mail — nothing else.
    """,
    'author': 'O&A Beauty / Migration Project',
    'website': 'https://www.oabeauty.example',
    'depends': [
        'website',
        'website_sale',
        'mail',
    ],
    'data': [
        'data/product_attribute_data.xml',
        'data/product_public_category_data.xml',
        'data/website_data.xml',
        'views/website_templates.xml',
        'views/product_template_backend_views.xml',
        'views/website_sale_product_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'oa_beauty_theme/static/src/scss/oa_beauty.scss',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
