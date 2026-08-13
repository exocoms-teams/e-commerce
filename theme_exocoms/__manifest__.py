{
    "name": "Theme EXOCOMS",
    "summary": "Site vitrine EXOCOMS - integrateur monetique, informatique, reseaux et securite",
    "version": "19.0.1.0.0",
    "category": "Theme/Corporate",
    "author": "EXOCOMS",
    "license": "LGPL-3",
    "depends": ["website", "website_crm"],
    "data": [
        "views/layout.xml",
        "views/pages.xml",
    ],
    "assets": {
        # Nom exact du bundle : web.assets_frontend, SANS tiret bas.
        # Avec un nom errone le module s'installe sans erreur mais aucun
        # asset n'est charge : le site apparait sans style ni script.
        "web.assets_frontend": [
            "theme_exocoms/static/src/scss/main.scss",
        ],
    },
    "installable": True,
    "application": False,
}
