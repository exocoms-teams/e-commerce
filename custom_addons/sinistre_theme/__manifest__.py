{
    'name': 'Sinistre Services — Theme',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Theme officiel Sinistre Services — urgence, artisans, assurances',
    'author': 'exocoms',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates/layout.xml',
        'views/templates/components.xml',
        'views/pages/home.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'sinistre_theme/static/src/css/main.css',
        ],
    },
    'installable': True,
    'application': False,
}
