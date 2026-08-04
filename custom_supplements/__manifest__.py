{
   'name': 'Boutique Compléments Alimentaires',
    'author': 'Yassine Tartor',
    'license': 'LGPL-3',
    'version': '1.0',
    'summary': 'Extension e-commerce pour la vente de compléments alimentaires',
    'category': 'eCommerce',
    'depends': [
        'base',
        'website_sale',
        'stock',
        'product_expiry', # Ajout du module de gestion des DLC/DLUO
    ],

        #bloc 'assets' pour charger votre futur design :
        'assets': {
        'web.assets_frontend': [
        'custom_supplements/static/src/js/allergen_filter.js',
            'custom_supplements/static/src/scss/style.scss',
        ],
    },
'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/ecommerce_categories.xml',
        'data/allergens.xml',
        'data/ecommerce_products.xml', # Nos produits de test
        'views/product_template_views.xml',
        'views/allergen_views.xml',
        # 'views/website_layout.xml',
        # 'views/website_sale_templates.xml',
        'views/website_product_template_views.xml',
        'views/website_homepage_views.xml',
    ],
    'installable': True,
    'application': True,
}