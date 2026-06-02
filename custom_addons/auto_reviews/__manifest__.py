{
    "name": "Automobile - Avis",
    "version": "1.0.3",
    "summary": "Avis clients avec modération",
    "category": "Website",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["website", "portal", "mail", "auto_base", "auto_website"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/auto_review_views.xml",
        "views/auto_review_templates.xml"
    ],
    "application": False,
    "installable": True
}
