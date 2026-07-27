{
    'name': 'Produits Tendance',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'author': 'winners',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale', 'auth_signup'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/trend_ad_views.xml',
        'views/website_templates.xml',
        'views/trend_product_views.xml',
        'views/trend_submission_views.xml',
        'views/trend_submission_templates.xml',
        'views/auth_templates.xml',   # WIN-47
        'views/trend_product_detail_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'produits_tendance/static/src/scss/_winners_variables.scss',
            'produits_tendance/static/src/scss/trend_submission_form.scss',
            'produits_tendance/static/src/scss/trend_product_detail.scss',
        ],
    },
    'installable': True,
    'application': False,
}