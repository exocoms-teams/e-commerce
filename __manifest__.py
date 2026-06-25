{
    "name": "Tire Catalog",
    "version": "1.0",
    "depends": ["product", "website_sale", "sale_management"],
    "author": "Thomas A.",
    "category": "Sales",
    "description": "Champs produits adaptés aux pneus.",
    "data": [
        "security/ir.model.access.csv",
        "views/category_views.xml",
        "views/product_template_views.xml",
        "views/website_product_views.xml",
        "data/product_category.xml",
        "data/tire_tread_pattern.xml",
        "data/tire_usage.xml",
        "demo/product_data.xml",
    ],
    "installable": True,
    "application": True,
    "icon": "/tire_catalog/static/description/icon.png",
    "license": "LGPL-3",
    "assets": {
        "web.assets_frontend": [
            "tire_catalog/static/src/css/style.css",
            # "tire_catalog/static/src/js/script.js",
        ],
    },
}
