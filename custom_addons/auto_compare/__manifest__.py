{
    "name": "Auto Compare",
    "version": "1.0.0",
    "summary": "Vehicle comparison feature",
    "category": "Website",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["website", "auto_base", "auto_website"],
    "data": [
        "views/auto_compare_templates.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "auto_compare/static/src/js/auto_compare.js"
        ]
    },
    "application": False,
    "installable": True
}
