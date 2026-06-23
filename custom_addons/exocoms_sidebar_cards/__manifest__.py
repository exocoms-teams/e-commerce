# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS - Sidebar de filtres (Modèle 1 - Cartes)",
    "summary": "Catégories repliables 3 niveaux, filtre marques, comparaison "
               "produits, curseur de prix et rafraîchissement AJAX. Snippet "
               "Website Builder + module complet. 100% Odoo 19 natif.",
    "version": "19.0.1.0.0",
    "author": "EXOCOMS Group",
    "website": "https://www.exocoms.fr",
    "category": "Website/eCommerce",
    "license": "LGPL-3",
    "depends": [
        "website_sale",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_brand_views.xml",
        "views/templates.xml",
        "views/snippets.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "exocoms_sidebar_cards/static/src/scss/filter_sidebar.scss",
            "exocoms_sidebar_cards/static/src/js/filter_sidebar.js",
        ],
        "website.website_builder_assets": [
            "exocoms_sidebar_cards/static/src/website_builder/sidebar_option.js",
            "exocoms_sidebar_cards/static/src/website_builder/sidebar_option.xml",
        ],
    },
    "images": ["static/description/thumb.svg"],
    "installable": True,
    "application": False,
}
