{
    'name': 'Telecom Services',
    'version': '19.0.1.0.2',
    'summary': 'Offre Télécom Dstny — méga-menu, catalogue /telecom, produits services',
    'author': 'Exocoms Group',
    'license': 'LGPL-3',
    'category': 'Website',
    'depends': [
        'website',
        'website_sale',
    ],
    'data': [
        'data/product_categories.xml',
        'data/products.xml',
        'data/menu_data.xml',
        'views/telecom_page.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'telecom_services/static/src/scss/telecom_mega_menu.scss',
            'telecom_services/static/src/js/telecom_mega_menu.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'post_migrate': 'post_migrate_hook',
    'installable': True,
    'application': False,
}
