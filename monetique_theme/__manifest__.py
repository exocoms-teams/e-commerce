# -*- coding: utf-8 -*-
{
    'name': 'PayCore — Infrastructure de Paiement',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Site vitrine premium pour solutions monétiques et paiement',
    'description': """
        Module website custom pour PayCore.
        Architecture complète : navbar premium, hero, services monétiques,
        sections métiers, footer enterprise, animations premium.
        Compatible Odoo 19 / Odoo.sh.
    """,
    'author': 'PayCore Dev Team',
    'website': 'https://paycore.fr',
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
            # Fonts (chargées via CSS @import dans main.scss)
            # SCSS — ordre strict : utils → layout → components → pages
            'paycore_website/static/src/scss/utils/_variables.scss',
            'paycore_website/static/src/scss/utils/_mixins.scss',
            'paycore_website/static/src/scss/utils/_animations.scss',
            'paycore_website/static/src/scss/layout/_reset.scss',
            'paycore_website/static/src/scss/layout/_base.scss',
            'paycore_website/static/src/scss/layout/_navbar.scss',
            'paycore_website/static/src/scss/layout/_footer.scss',
            'paycore_website/static/src/scss/layout/_grid.scss',
            'paycore_website/static/src/scss/components/_buttons.scss',
            'paycore_website/static/src/scss/components/_cards.scss',
            'paycore_website/static/src/scss/components/_badges.scss',
            'paycore_website/static/src/scss/components/_forms.scss',
            'paycore_website/static/src/scss/components/_sections.scss',
            'paycore_website/static/src/scss/pages/_home.scss',
            'paycore_website/static/src/scss/pages/_services.scss',
            'paycore_website/static/src/scss/pages/_contact.scss',
            # JS
            'paycore_website/static/src/js/main.js',
            'paycore_website/static/src/js/navbar.js',
            'paycore_website/static/src/js/animations.js',
            'paycore_website/static/src/js/counters.js',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
