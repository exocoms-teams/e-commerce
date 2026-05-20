{
    'name': 'monetiques.fr — Infrastructure de Paiement',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'author': 'monetiques.fr',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/products.xml',
        'views/templates/layout.xml',
        'views/templates/components.xml',
        'views/pages/home.xml',
        'views/pages/audit.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'monetique_theme/static/src/css/main.css',
        ],
    },
    'installable': True,
    'application': False,
}
