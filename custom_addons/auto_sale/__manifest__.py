{
    "name": "Auto Sale",
    "version": "1.0.2",
    "summary": "Automotive sales adaptation, quote requests, vehicle order bridge",
    "category": "Sales",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["sale_management", "website_sale", "crm", "mail", "auto_base"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/sequence.xml",
        "data/mail_templates.xml",
        "views/auto_quote_request_views.xml",
        "views/auto_sale_templates.xml"
    ],
    "application": False,
    "installable": True
}
