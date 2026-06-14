# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS — Sidebar Filter AJAX",
    "version": "19.0.2.0.0",
    "summary": "Filtrage dynamique AJAX sans rechargement — sidebar 3 niveaux, pagination, recherche, tri, prix",
    "author": "EXOCOMS Group",
    "website": "https://www.exocoms.com",
    "category": "Website/eCommerce",
    "license": "LGPL-3",
    "depends": ["website_sale", "website", "product"],
    "data": [
        "views/sidebar_filter_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "exocoms_sidebar_ajax/static/src/css/sidebar_filter.scss",
            "exocoms_sidebar_ajax/static/src/js/sidebar_filter.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
