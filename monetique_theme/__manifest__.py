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
            # Fonts (chargées via CSS @import dans main.scss)
            # SCSS — ordre strict : utils → layout → components → pages
            'monetique_theme/static/src/scss/utils/_variables.scss',
            'monetique_theme/static/src/scss/utils/_mixins.scss',
            'monetique_theme/static/src/scss/utils/_animations.scss',
            'monetique_theme/static/src/scss/layout/_reset.scss',
            'monetique_theme/static/src/scss/layout/_base.scss',
            'monetique_theme/static/src/scss/layout/_navbar.scss',
            'monetique_theme/static/src/scss/layout/_footer.scss',
            'monetique_theme/static/src/scss/layout/_grid.scss',
            'monetique_theme/static/src/scss/components/_buttons.scss',
            'monetique_theme/static/src/scss/components/_cards.scss',
            'monetique_theme/static/src/scss/components/_badges.scss',
            'monetique_theme/static/src/scss/components/_forms.scss',
            'monetique_theme/static/src/scss/components/_sections.scss',
            'monetique_theme/static/src/scss/pages/_home.scss',
            'monetique_theme/static/src/scss/pages/_services.scss',
            'monetique_theme/static/src/scss/pages/_contact.scss',
            # JS
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
