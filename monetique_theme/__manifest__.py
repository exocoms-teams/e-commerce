{
    'name': 'monetiques.fr — Infrastructure de Paiement',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'author': 'monetiques.fr',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale'],

    'data': [
        'security/ir.model.access.csv',

        'views/templates/header.xml',
        'views/templates/footer.xml',
        'views/templates/search.xml',
        'views/templates/layout.xml',
        'views/templates/hero.xml',
        'views/templates/categories.xml',
        'views/templates/popular_products.xml',
        'views/templates/product_card.xml',
        'views/templates/feature_cards.xml',
        'views/templates/brands.xml',
        'views/templates/newsletter.xml',
        


        'views/pages/home.xml',
    ],

    'assets': {
        'web.assets_frontend': [

            'monetique_theme/static/src/css/variables.css',
            'monetique_theme/static/src/css/layout.css',
            'monetique_theme/static/src/css/home.css',
            'monetique_theme/static/src/css/shop.css',
            'monetique_theme/static/src/css/product.css',
            'monetique_theme/static/src/css/responsive.css',
            'monetique_theme/static/src/css/animations.css',
            'monetique_theme/static/src/css/main.css',

            'monetique_theme/static/src/js/slider.js',

        ],
    },

    'installable': True,
    'application': False,
}
