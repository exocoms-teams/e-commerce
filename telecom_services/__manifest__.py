{
    'name': 'Telecom Services',
    'version': '19.0.1.0.0',
    'summary': 'Mega-menu Télécom et catalogue de services Dstny',
    'category': 'Website',
    'author': 'Exocoms',
    'website': 'https://exocoms.fr',
    'depends': ['website', 'website_sale'],
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
    'post_migrate_hook': 'post_migrate_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
