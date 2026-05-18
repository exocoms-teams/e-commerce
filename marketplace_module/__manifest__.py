{
    'name': 'Marketplace Multi-Vendeurs',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Place de marche multi-vendeurs pour monetiques.fr',
    'author': 'monetiques.fr',
    'license': 'LGPL-3',

    'depends': ['website', 'website_sale', 'portal'],

    'data': [
        'security/marketplace_security.xml',
        'security/ir.model.access.csv',
        'views/vendor_views.xml',
        'views/product_extension_views.xml',
        'views/vendor_portal.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'marketplace_module/static/src/css/marketplace.css',
        ],
    },

    'installable': True,
    'application': False,  # Pas une application autonome, c'est une extension
    'auto_install': False,
}
