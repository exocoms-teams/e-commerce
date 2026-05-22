# -*- coding: utf-8 -*-
{
    'name': 'planet Mobil- Website Planet Mobil',
    'version': '19.0.1.0.2',
    'category': 'Website/eCommerce',
    'summary': 'Page d\'accueil e-commerce Planet Mobil',
    'author': 'Planet Mobil',
    'depends': ['website', 'web', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'templates/header.xml',
        'templates/footer.xml',
        'templates/homepage.xml',
        'templates/avis_page.xml',
        'templates/contact_page.xml',
        'templates/category_page.xml',
        'templates/product_page.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_planet_mobil/static/src/css/style.css',
        ],
        'web.assets_frontend_minimal': [
            'website_planet_mobil/static/src/js/main.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
