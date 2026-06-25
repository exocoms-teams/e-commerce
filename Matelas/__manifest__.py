# -*- coding: utf-8 -*-
{
    'name': 'Matelas',
    'version': '19.0.1.0.10',
    'summary': 'Site e-commerce de vente de matelas',
    'category': 'Website',
    'depends': ['website', 'website_sale'],
    'author': 'Equipe matelas',
    'license': 'LGPL-3',

    'data': [
        'views/templates/Home.xml',
        'views/templates/Avis.xml',
        'views/templates/Contact.xml',
        'views/templates/Mentions_légales.xml',
        'data/Footer.xml',
        'data/Header.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
            'Matelas/static/src/css/Home.css',
            'Matelas/static/src/css/Avis.css',
            'Matelas/static/src/css/Contact.css',
            'Matelas/static/src/css/Mentions.css',
            'Matelas/static/src/js/main.js',  
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,

}
