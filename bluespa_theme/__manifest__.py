{
    'name': 'BlueSpa Theme',
    'version': '19.0.1.0.0',
    'category': 'Website/Theme',
    'summary': "Thème du site eCommerce BlueSpa — vente de spas",
    'description': """
BlueSpa Theme
=============
Page d'accueil, snippets et habillage boutique pour le site eCommerce
BlueSpa (vente de spas), construits en code pour survivre aux
rebuilds de la branche Odoo.sh.
""",
    'author': 'EXOCOMS GROUP',
    'depends': ['website', 'website_sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/snippets/snippets.xml',
        'views/snippets/s_bluespa_hero.xml',
        'views/snippets/s_bluespa_why_us.xml',
        'views/snippets/s_bluespa_catalog.xml',
        'views/snippets/s_bluespa_reviews.xml',
        'views/pages/homepage.xml',
        'views/layout/footer.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'assets': {
        'web.assets_frontend': [
            'bluespa_theme/static/src/scss/variables.scss',
            'bluespa_theme/static/src/scss/s_bluespa_hero.scss',
            'bluespa_theme/static/src/scss/s_bluespa_why_us.scss',
            'bluespa_theme/static/src/scss/s_bluespa_catalog.scss',
            'bluespa_theme/static/src/scss/s_bluespa_reviews.scss',
            'bluespa_theme/static/src/scss/footer.scss',
            'bluespa_theme/static/src/scss/shop.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
