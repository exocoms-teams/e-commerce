{
    "name": "Automobile - Site web",
    "version": "1.0.6",
    "summary": "Pages publiques du site automobile",
    "category": "Website",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["website", "website_sale", "portal", "auto_base"],
    "data": [
        "data/website_menu_cleanup.xml",
        "views/auto_website_templates.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "auto_website/static/src/scss/auto_website.scss",
            "auto_website/static/src/js/auto_website.js"
        ]
    },
    "application": False,
    "installable": True
}
