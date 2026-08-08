# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS - Marque blanche (Debranding Odoo)",
    "version": "19.0.2.0.0",
    "category": "Technical",
    "summary": "Remplace les mentions « Powered by Odoo » par votre propre marque "
               "(texte, logo, lien) dans le portail, les e-mails et les rapports PDF.",
    "description": """
Marque blanche EXOCOMS
======================

Remplace — ou supprime — les mentions promotionnelles Odoo (« Powered by Odoo »,
« Propulsé par Odoo », « Sent by ... using Odoo », liens vers odoo.com, balise
meta generator) dans :

* toutes les pages du portail et du site web (frontend) ;
* tous les e-mails sortants (layouts de notification, templates) ;
* tous les rapports QWeb / PDF : devis, bons de commande, factures, BL... ;
* le back-office : titre de l'onglet navigateur et entrées Odoo du menu utilisateur.

En mode « Remplacer », le bloc d'origine est conservé (position, alignement,
style) et son contenu est remplacé par votre accroche, votre logo et votre lien.

Le paramétrage est **par société** : une instance multi-société peut donc
afficher une marque différente pour chaque client hébergé.

Le nettoyage est effectué au niveau du moteur de rendu QWeb (`ir.qweb._render`),
ce qui le rend indépendant des identifiants de templates : aucune surcharge XML
fragile, aucun risque de casse lors d'une montée de version.

Configuration : Paramètres > Technique > Marque blanche.
Interrupteur général : paramètre système `exocoms_debranding.enabled`.
""",
    "author": "EXOCOMS Group",
    "website": "https://exocoms.fr",
    "license": "LGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_company_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "exocoms_debranding/static/src/js/debrand_backend.js",
        ],
        "web.assets_frontend": [
            "exocoms_debranding/static/src/scss/debrand_frontend.scss",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
