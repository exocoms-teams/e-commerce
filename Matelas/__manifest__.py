# -*- coding: utf-8 -*-
{
    'name': 'Matelas',
    'version': '19.0.1.0.10',
    'summary': 'Site e-commerce de vente de matelas',
    'category': 'Website',
    'depends': ['website', 'website_sale'],
    'data': [
        'views/templates/Home.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'Matelas/static/src/css/Home.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}
