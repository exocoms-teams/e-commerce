{
    'name': 'O&A Beauty Theme',
    'version': '19.0.3.0.0',
    'category': 'Website/Theme',
    'summary': 'LUMIERE frontend for Odoo 19: homepage, shop, product page, brand SCSS',
    'description': 'Full migration of the LUMIERE cosmetics frontend to Odoo 19.',
    'author': 'O&A Beauty',
    'website': 'https://www.oabeauty.example',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
        'mail',
    ],
    'data': [
        'data/product_attribute_data.xml',
        'data/product_public_category_data.xml',
        'views/website_templates.xml',
        'views/website_homepage.xml',
        'data/website_data.xml',
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
}
