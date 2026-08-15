{
    'name': 'Theme EXOCOMS',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'author': 'monetiques.fr',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale','website_crm'],

    'data': [
        'security/ir.model.access.csv',

        'views/pages/home1.xml',

        'views/templates/header.xml',
        'views/templates/footer.xml',
        'views/templates/layout.xml',

        
    ],

    'assets': {
        'web.assets_frontend': [
            'monetique_theme/static/src/css/templates/header.css',
            'monetique_theme/static/src/css/templates/footer.css',
            'monetique_theme/static/src/css/pages/home1.css',
        ],
    },
    'installable': True,
    'application': False,
}
