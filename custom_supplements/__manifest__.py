{
    'name': 'Boutique Compléments Alimentaires',
    'author': 'Yassine Tartor',
    'license': 'LGPL-3',
    'version': '1.0',
    'summary': 'Extension e-commerce pour la vente de compléments alimentaires',
    'category': 'eCommerce',
    'depends': [
        'base',
        'product',
        'website_sale',
        'stock',
        'product_expiry', # Ajout du module de gestion des DLC/DLUO
        'exocoms_rgpd'
    ],

    # Bloc 'assets' mis à jour pour respecter le builder Odoo 19 :
    'assets': {
        # 1. Variables globales (couleurs, typos) prioritaires sur Bootstrap
        'web._assets_primary_variables': [
            ('prepend', 'custom_supplements/static/src/scss/primary_variables.scss'),
        ],
        
        # 2. Ton design spécifique
        'web.assets_frontend': [
            'custom_supplements/static/src/scss/style.scss',
        ],

        'web.assets_backend': [
            'custom_supplements/static/src/scss/backend.scss',
        ],
    },
    
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/ecommerce_categories.xml',
        'data/allergens.xml',
        'data/ecommerce_products.xml', # Nos produits de test
        'data/website_menus.xml',
        'views/product_template_views.xml',
        'views/allergen_views.xml',
        'views/website_layout.xml',
        'views/website_sale_templates.xml',
        'views/website_product_template_views.xml',
        'views/website_homepage_views.xml',
    ],
    'installable': True,
    'application': True,
    'post_init_hook': 'post_init_hook',
}