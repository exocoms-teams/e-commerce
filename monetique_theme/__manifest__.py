{
    'name': 'monetiques.fr — Infrastructure de Paiement',
    'version': '19.0.1.0.0',
    'author': 'monetiques.fr',
    'license': 'LGPL-3',
    'category': 'Theme/eCommerce',
    'depends': ['website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/ecommerce_categories.xml',
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
