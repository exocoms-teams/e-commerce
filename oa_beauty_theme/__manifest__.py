{
    'name': 'O.A.I Beauty Theme',
    'version': '19.0.7.0.0',
    'category': 'Website/Theme',
    'summary': 'O.A.I Beauty frontend for Odoo 19: homepage, shop, product page, brand SCSS',
    'description': 'Full migration of the O.A.I Beauty cosmetics frontend to Odoo 19. Clean Luxury positioning.',

    'author': 'O.A.I Beauty',
    'website': 'https://www.oaibeauty.example',
    'license': 'LGPL-3',

    'depends': [
        'website',
        'website_sale',
        'website_blog',
        'mail',
        'delivery',
        'base_setup',
    ],

    # ---------------------------
    # DATA (ORDER FIXED)
    # ---------------------------
    'data': [
        'security/ir.model.access.csv',

        'data/delivery_data.xml',
        'data/product_attribute_data.xml',
        'data/product_public_category_data.xml',
        'data/cleanup_data.xml',
        'data/product_data.xml',
        'data/oa_products.xml',
        'data/fragrance_data.xml',
        'data/mail_template_data.xml',
        'data/blog_data.xml',
        'data/ingram_cron.xml',

        'views/website_templates.xml',
        'views/website_navigation_templates.xml',
        'views/website_homepage.xml',
        'views/analytics_templates.xml',
        'views/website_advisor_templates.xml',
        'views/website_chatbot_templates.xml',
        'views/res_config_settings_views.xml',

        'views/product_template_backend_views.xml',
        'views/website_sale_product_templates.xml',
        'views/website_sale_cart_templates.xml',
        'views/website_sale_checkout_templates.xml',
        'views/website_core_pages.xml',
        'views/portal_templates.xml',
        'views/auth_templates.xml',
    ],

    # ---------------------------
    # ASSETS (FIXED FOR ODOO 19)
    # ---------------------------
    'assets': {
        'web.assets_frontend': [
            'oa_beauty_theme/static/src/scss/oa_beauty.scss',
            'oa_beauty_theme/static/src/js/advisor.js',
            'oa_beauty_theme/static/src/js/chatbot.js',
        ],
    },

    # ---------------------------
    # OPTIONAL BUT USEFUL
    # ---------------------------
    'installable': True,
    'application': False,

    # helps during dev (avoids cache confusion)
    'auto_install': False,
}