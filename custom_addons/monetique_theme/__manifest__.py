# -*- coding: utf-8 -*-
{
    'name': 'Monétiques Theme',
    'version': '17.0.1.0',
    'category': 'Website/Theme',
    'summary': 'Thème officiel monetiques.fr — frontend complet',
    'description': 'Reconstruction complète du frontend monetiques.fr avec design system exact.',
    'author': 'monetiques.fr',
    'website': 'https://monetiques.fr',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/layout_templates.xml',
        'views/homepage_templates.xml',
        'views/pages_templates.xml',
        'views/shop_templates.xml',
        'data/website_data.xml',
    ],
    'assets': {
        'website.assets_frontend': [
            '/monetique_theme/static/src/css/variables.css',
            '/monetique_theme/static/src/css/base.css',
            '/monetique_theme/static/src/css/layout.css',
            '/monetique_theme/static/src/css/homepage.css',
            '/monetique_theme/static/src/css/pages.css',
            '/monetique_theme/static/src/css/shop.css',
            '/monetique_theme/static/src/js/main.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
