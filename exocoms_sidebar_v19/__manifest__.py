# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS — Sidebar Filter",
    "version": "19.0.1.0.0",
    "summary": "Panneau latéral de filtrage 3 niveaux pour le site web Odoo 19",
    "author": "EXOCOMS Group",
    "website": "https://www.exocoms.com",
    "category": "Website/eCommerce",
    "license": "LGPL-3",

    # Odoo 19 : website_sale_stock n'existe plus en tant que module séparé
    "depends": [
        "website_sale",
        "website",
        "product",
    ],

    "data": [
        "views/sidebar_filter_templates.xml",
    ],

    "assets": {
        # Odoo 19 : les assets frontend passent par web.assets_frontend
        "web.assets_frontend": [
            "exocoms_sidebar_v19/static/src/css/sidebar_filter.scss",
            "exocoms_sidebar_v19/static/src/js/sidebar_filter.js",
        ],
    },

    "installable": True,
    "auto_install": False,

    # Odoo 19 : champ obligatoire
    "application": False,
}
