# -*- coding: utf-8 -*-
{
    'name': 'Boat Services',
    'version': '16.0.1.0.0',
    'summary': 'Site vitrine et e-commerce pour bateaux',
    'description': '''
Module Odoo pour présenter des bateaux, afficher leurs caractéristiques
et récupérer les demandes de prix, de catalogue ou de contact.
''',
    'author': 'Exocoms - Yasmine',
    'category': 'Website/eCommerce',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
        'product',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/product_views.xml',
        'views/boat_inquiry_views.xml',
        'views/website_templates.xml',
        'data/website_menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'boat_services/static/src/css/boat_services.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
