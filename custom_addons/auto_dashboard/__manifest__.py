{
    "name": "Auto Dashboard",
    "version": "1.0.0",
    "summary": "Automotive business KPIs",
    "category": "Reporting",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["sale_management", "crm", "auto_base", "auto_sale", "auto_booking", "auto_reviews"],
    "data": [
        "security/ir.model.access.csv",
        "views/auto_dashboard_views.xml"
    ],
    "application": False,
    "installable": True
}
