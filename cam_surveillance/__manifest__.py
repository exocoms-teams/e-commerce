# -*- coding: utf-8 -*-
{
    'name': 'Cam Surveillance Shop',
    'version': '19.0.1.0.0',
    'category': 'Website/eCommerce',
    'summary': 'Boutique e-commerce caméras de surveillance AXIS',
    'author': 'Johnny Farrane',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale', 'monetique_theme', 'stock'],
    'data': [
        # Data
        'data/website_data.xml',
        'data/categories.xml',
        'data/attributs.xml',
        'data/products.xml',

        # Views
        'views/reasurance_banner.xml',
        'views/layout.xml',

        # Views items
        'views/items/card_product.xml',
        
        # Views home
        'views/home/hero.xml',
        'views/home/brands.xml',
        'views/home/categories.xml',
        'views/home/products.xml',
        'views/home/reviews.xml',
        'views/home/why.xml',
        
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