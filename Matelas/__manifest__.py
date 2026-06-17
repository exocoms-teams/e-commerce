# -*- coding: utf-8 -*-
{
    'name': 'Matelas',
    'version': '1.0',
    'summary': 'Site e-commerce de vente de matelas',
    'category': 'Website',
    'depends': ['website', 'website_sale'],
    'data': [
        'views/Home.xml',
    ],
    'installable': True,
    'application': True,
}

'assets': {
    'web.assets_frontend': [
        'Matelas/static/src/css/.css',
    ],
},
