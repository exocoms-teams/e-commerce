{
    "name": "Exocoms Ingram API",
    "version": "19.0.1.0.0",
    "summary": "Connecteur API Ingram Micro pour Exocoms",
    "author": "Exocoms",
    "category": "Inventory",
    "depends": ["base_setup", "product", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
        "views/ingram_search_wizard_views.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
