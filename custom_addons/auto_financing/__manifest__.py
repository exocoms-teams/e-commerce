{
    "name": "Auto Financing",
    "version": "1.0.0",
    "summary": "Vehicle financing requests (phase 2)",
    "category": "Sales",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["website", "portal", "mail", "auto_base"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/auto_financing_request_views.xml",
        "views/auto_financing_templates.xml"
    ],
    "application": False,
    "installable": True
}
