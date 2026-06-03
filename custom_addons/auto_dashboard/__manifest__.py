{
    "name": "Automobile - Tableau de bord",
    "version": "1.0.2",
    "summary": "Indicateurs commerciaux automobiles",
    "category": "Reporting",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "crm",
        "spreadsheet_dashboard",
        "auto_base",
        "auto_sale",
        "auto_booking",
        "auto_financing",
        "auto_reviews",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/auto_dashboard_data.xml",
        "views/auto_dashboard_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "auto_dashboard/static/src/scss/auto_dashboard.scss",
        ]
    },
    "application": False,
    "installable": True
}
