{
    'name': 'Telecom Services',
    'version': '19.0.3.0.0',
    'summary': 'Vitrine catalogue Télécom KISSGROUP (commande sur portail KISSGROUP)',
    'category': 'Website',
    'author': 'Exocoms',
    'website': 'https://exocoms.fr',
    'depends': ['website', 'website_sale'],
    'data': [
        'data/menu_data.xml',
        'data/translations_fr.xml',
        'data/translations_en.xml',
        'data/kissgroup_data.xml',
        'views/telecom_page.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'telecom_services/static/src/scss/telecom_mega_menu.scss',
            'telecom_services/static/src/js/telecom_mega_menu.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
