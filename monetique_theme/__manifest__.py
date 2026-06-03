# -*- coding: utf-8 -*-
{
    'name': 'Monetique Theme',
    'version': '19.0.2.0.0',
    'category': 'Website',
    'summary': 'Site vitrine professionnel pour services monétiques',
    'author': 'Exocoms',
    'depends': ['website', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/layout.xml',
        'views/home.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'monetique_theme/static/src/css/style.css',
            'monetique_theme/static/src/js/main.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
