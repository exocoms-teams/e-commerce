# EXOCOMS - Sinistre Services — Infrastructure de gestion d intervention
{
    'name': 'Sinistre Services — Infrastructure de gestion d intervention',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Sinistre Services — urgence, artisans, assurances',
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
            'monetique_theme/static/src/css/main.css',
        ],
    },
    'installable': True,
    'application': False,
}
