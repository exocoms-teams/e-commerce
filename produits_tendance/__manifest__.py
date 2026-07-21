{
    'name': 'Produits Tendance',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'author': 'winners',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale'],

    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/trend_ad_views.xml',
        'views/website_templates.xml',
        'views/trend_product_views.xml',
    ],

    'installable': True,
    'application': False,
}