{
    'name': "Caractéristiques produit",
    'version': '19.0.5.2.0',
    'summary': "Caractéristiques techniques structurées, récupération automatique sur internet, "
               "calcul des frais de port et comparaison produits.",
    'description': """
Caractéristiques produit
=========================

Fonctionnalités
---------------

* Catégories et caractéristiques réutilisables (Connectivité, Écran, Système, Sécurité…)
* Onglet "Caractéristiques" sur la fiche produit
* Récupération automatique des specs sur internet (poids, dimensions, caractéristiques)
* Calcul des frais de port multi-transporteurs (API temps réel ou grille statique)
* Assistant de création de transporteur (clé API ou grille tarifaire manuelle)
* Import en masse au format "Catégorie ; Caractéristique ; Valeur"
* Tableau des caractéristiques sur la fiche produit du site e-commerce
* Impression PDF (fiche seule avec QR code, comparatif A4 paysage)
* Partage (lien, email, WhatsApp, Web Share API)
* Page de comparaison multi-produits

Compatibilité : Odoo 19 / Odoo.sh
""",
    'category': 'Sales/Sales',
    'author': "EXOCOMS Group",
    'website': "https://exocoms.fr",
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'product',
        'sale',
        'sale_management',
        'stock',
        'delivery',
        'website_sale',
    ],
    'external_dependencies': {
        'python': ['requests', 'bs4', 'lxml'],
    },
    'data': [
        # 1. Sécurité en premier
        'security/ir.model.access.csv',

        # 2. Vues de configuration (définissent les menus racines)
        'views/product_spec_views.xml',

        # 3. Wizards (définissent les actions référencées par les vues)
        'wizard/product_spec_import_wizard_views.xml',
        'wizard/product_spec_fetch_wizard_views.xml',
        'wizard/product_spec_carrier_create_wizard_views.xml',

        # 4. Vues transporteurs (référencent menu racine + action wizard)
        'views/product_spec_carrier_views.xml',
        'views/product_spec_quality_views.xml',
        'views/product_spec_lifecycle_views.xml',
        'views/product_spec_marketplace_views.xml',
        'views/delivery_carrier_views.xml',
        'views/sale_order_views.xml',

        # 5. Vues produit (référencent l'action fetch wizard)
        'views/product_template_views.xml',

        # 6. Templates site web
        'views/product_spec_compare_templates.xml',
        'views/shop_spec_filter_templates.xml',
        'views/product_spec_social_templates.xml',

        # 7. Rapports PDF
        'report/product_spec_single_report.xml',
        'report/product_spec_compare_report.xml',
        'report/product_catalog_report.xml',

        # 8. Données de démarrage (après les modèles et vues)
        'data/product_spec_data.xml',
        'data/product_spec_carrier_data.xml',
        'data/product_spec_cron.xml',
        'data/product_spec_marketplace_cron.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'product_spec_sheet/static/src/js/product_spec_share.js',
            'product_spec_sheet/static/src/js/shop_spec_filter.js',
            'product_spec_sheet/static/src/css/product_spec_share.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
