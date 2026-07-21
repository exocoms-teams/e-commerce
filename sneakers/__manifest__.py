{
    'name': 'monetiques.fr — Infrastructure de Paiement',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'author': 'monetiques.fr',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale'],

    'data': [
        'security/ir.model.access.csv',

        '/views/templates/layout.xml',
        '/views/templates/header.xml',
        '/views/templates/footer.xml',
        '/views/templates/product_card.xml',
        

        '/views/pages/home.xml',
        '/views/pages/shop.xml',
        '/views/pages/product.xml',
        '/views/pages/cart.xml',
        '/views/pages/checkout.xml',
        '/views/pages/confirmation.xml',
    ],

    'assets': {
        'web.assets_frontend': [

            'sneakers/static/src/css/variables.css',
            'sneakers/static/src/css/layout.css',

            'sneakers/static/src/css/home.css',
            'sneakers/static/src/css/shop.css',
            'sneakers/static/src/css/product.css',
            'sneakers/static/src/css/cart.css',
            'sneakers/static/src/css/checkout.css',
            'sneakers/static/src/css/confirmation.css',

            'sneakers/static/src/css/footer.css',
            'sneakers/static/src/css/responsive.css',
            'sneakers/static/src/css/animations.css',
            'sneakers/static/src/css/main.css',

            'sneakers/static/src/js/slider.js',

        ],
    },

    'installable': True,
    'application': False,
}
