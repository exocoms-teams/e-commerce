# -*- coding: utf-8 -*-
{
    'name': 'monetiques.fr — Infrastructure de Paiement',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Site vitrine premium pour solutions monétiques et paiement',
    'description': """
        Module website custom pour monetiques.fr.
        Architecture complète : navbar premium, hero, services monétiques,
        sections métiers, footer enterprise, animations premium.
        Compatible Odoo 19 / Odoo.sh.
    """,
    'author': 'monetiques.fr Dev Team',
    'website': 'https://monetiques.fr',
    'license': 'LGPL-3',

    'depends': [
        'website',
        'mail',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/website_data.xml',
        'views/templates/layout.xml',
        'views/templates/components.xml',
        'views/pages/home.xml',
        'views/pages/services.xml',
        'views/pages/contact.xml',
        'views/pages/about.xml',
        'views/pages/tpe.xml',
        'views/pages/encaissement.xml',
        'views/pages/support.xml',
        'views/pages/omnicanal.xml',
        'views/menus.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'monetique_theme/static/src/css/main.css',
            'monetique_theme/static/src/js/main.js',
            'monetique_theme/static/src/js/navbar.js',
            'monetique_theme/static/src/js/animations.js',
            'monetique_theme/static/src/js/counters.js',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
