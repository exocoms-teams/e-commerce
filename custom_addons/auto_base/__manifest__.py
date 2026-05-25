{
    "name": "Auto Base",
    "version": "1.0.0",
    "summary": "Core automotive data models for Chinese car ecommerce",
    "category": "Website",
    "author": "Ecommerce Voitures Team",
    "license": "LGPL-3",
    "depends": ["base", "mail", "product", "website"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/auto_brand_views.xml",
        "views/auto_motorization_views.xml",
        "views/auto_vehicle_category_views.xml",
        "views/auto_vehicle_color_views.xml",
        "views/auto_vehicle_option_views.xml",
        "views/auto_vehicle_views.xml",
        "views/product_template_views.xml",
        "demo/demo_data.xml"
    ],
    "application": True,
    "installable": True
}
