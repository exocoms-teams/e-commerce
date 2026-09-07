# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS Debranding",
    "summary": "Suppression complète du branding Odoo (Odoo 19 uniquement)",
    "description": """
Debranding Odoo 19
==================

Remplace l'identité Odoo par celle de l'éditeur / intégrateur :

* titre de l'onglet navigateur et titre des pages backend / frontend ;
* liens « Powered by Odoo », « Odoo.com », « Manage Databases » ;
* entrées « Documentation », « Support », « Mon compte Odoo » du menu utilisateur ;
* titres des boîtes de dialogue d'erreur (« Odoo Server Error », ...) ;
* logo, favicon et icônes PWA remplacés par ceux de la société ;
* mode multi-société : marque, logo et URL résolus par société au rendu ;
* nom de l'application PWA (manifest.webmanifest) ;
* pied de page des courriels de notification ;
* désactivation du cron de notification éditeur (publisher warranty).

Le patch des templates QWeb est dynamique : le module scanne les vues à
l'installation et ne crée que les héritages qui s'appliquent réellement.
Aucun échec d'installation si un template Odoo change de structure.
""",
    "version": "19.0.2.0.0",
    "category": "Technical Settings",
    "author": "EXOCOMS Group",
    "website": "https://www.exocoms.fr",
    "license": "LGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_config_settings_views.xml",
        "views/web_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "exocoms_debranding/static/src/js/debranding.js",
            "exocoms_debranding/static/src/scss/backend.scss",
        ],
        "web.assets_frontend": [
            "exocoms_debranding/static/src/scss/frontend.scss",
        ],
    },
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
