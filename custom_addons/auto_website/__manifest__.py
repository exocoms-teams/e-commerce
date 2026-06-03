{
    "name": "Automobile - Site web",
    "version": "1.0.13",
    "summary": "Pages publiques du site automobile",
    "category": "Website",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["website", "website_sale", "portal", "auto_base"],
    "data": [
        "views/auto_website_templates.xml",
        "data/product_publish_sync.xml",
        "data/website_menu_cleanup.xml"
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
