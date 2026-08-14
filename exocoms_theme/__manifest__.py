{
    'name': 'Theme EXOCOMS',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'author': 'monetiques.fr',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale','website_crm'],

    'data': [
        'security/ir.model.access.csv',

        'views/layout.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'exocoms_theme/static/src/scss/main.scss',
        ],
    },
    'installable': True,
    'application': False,
}
