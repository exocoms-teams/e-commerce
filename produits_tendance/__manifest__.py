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
        'views/dashboard_templates.xml',   # WIN-48
    ],
    'assets': {
        'web.assets_frontend': [
            'produits_tendance/static/src/scss/_winners_variables.scss',
            'produits_tendance/static/src/scss/trend_submission_form.scss',
            'produits_tendance/static/src/scss/trend_product_detail.scss',
            'produits_tendance/static/src/scss/trend_chart.scss',
            # WIN-52 : Chart.js + adaptateur Luxon, déjà bundlés par Odoo (web).
            'web/static/lib/luxon/luxon.js',
            'web/static/lib/Chart/Chart.js',
            'web/static/lib/chartjs-adapter-luxon/chartjs-adapter-luxon.js',
            'produits_tendance/static/src/js/trend_chart.js',
            'produits_tendance/static/src/scss/dashboard.scss',
        ],
    },
    'installable': True,
    'application': False,
}