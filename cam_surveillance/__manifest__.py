# -*- coding: utf-8 -*-
{
    'name': 'Cam Surveillance Shop',
    'version': '19.0.1.0.0',
    'category': 'Website/eCommerce',
    'summary': 'Boutique e-commerce caméras de surveillance AXIS',
    'author': 'Johnny Farrane',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale', 'monetique_theme'],
    'data': [
        'data/website_data.xml',
        'data/products.xml',
        'views/layout.xml',
        'views/home.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'cam_surveillance/static/src/css/cam_surveillance.css',
            'cam_surveillance/static/src/js/main.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}