{
    'name': 'O&A Beauty — Clean Luxury Cosmetics Theme',
    'version': '19.0.2.0.0',
    'category': 'Website/Theme',
    'summary': 'Luxury cosmetics theme',
    'description': 'Luxury cosmetics theme for Odoo 19.',
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
