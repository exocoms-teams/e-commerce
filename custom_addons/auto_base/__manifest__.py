{
    "name": "Automobile - Base",
    "version": "1.1.2",
    "summary": "Modèles de données automobiles pour l'e-commerce de voitures chinoises",
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
        "demo/demo_data.xml",
        "data/catalog_expansion.xml"
    ],
    "application": True,
    "installable": True
}
