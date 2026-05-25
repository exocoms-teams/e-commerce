{
    "name": "Auto Reviews",
    "version": "1.0.1",
    "summary": "Customer reviews with moderation",
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
