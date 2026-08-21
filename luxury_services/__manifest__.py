{
    'name': 'Luxury Services',
    'version': '19.0.1.0.0',
    'summary': 'Gestion des yachts, jets et services VIP',
    'author': 'Exocoms',
    'category': 'eCommerce',
    'depends': ['product', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/reservation_views.xml',
        'views/templates.xml',
        'views/luxury_destination_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'luxury_services/static/src/scss/custom.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}