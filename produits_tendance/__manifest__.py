{
    'name': 'Produits Tendance',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'author': 'winners',
    'license': 'LGPL-3',
    'depends': [
        'website', 'website_sale', 'auth_signup',
        'sale_subscription', 'website_sale_subscription',   # WIN-66
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/trend_ad_views.xml',
        'views/website_templates.xml',
        'views/trend_product_views.xml',
        'views/trend_submission_views.xml',
        'views/ebay_collection_templates.xml',
        'views/trend_submission_templates.xml',
        'views/auth_templates.xml',   # WIN-47
        'views/trend_product_detail_templates.xml',
        'data/subscription_plans.xml',           # WIN-66
        'data/subscription_products.xml',        # WIN-66
        'views/subscription_templates.xml',      # WIN-66
        'views/dashboard_templates.xml',   # WIN-48
        'data/webhook_queue_cron.xml',      # WIN-67
    ],
    'assets': {
        'web.assets_frontend': [
            'produits_tendance/static/src/scss/_winners_variables.scss',
            'produits_tendance/static/src/js/dashboard_ingestion.js',
            'produits_tendance/static/src/scss/trend_submission_form.scss',
            'produits_tendance/static/src/scss/trend_product_detail.scss',
            'produits_tendance/static/src/scss/subscription_pricing.scss',
            'produits_tendance/static/src/scss/dashboard.scss',
        ],
    },
    'installable': True,
    'application': False,
}