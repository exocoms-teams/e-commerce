{
    'name': 'Travel Agency',
    'version': '1.0',
    'author': 'ARMOD07',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': ['base', 'product', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/email_template.xml',
        'views/travel_product_views.xml',
        'views/travel_reservation_views.xml',
        'views/payment_provider_views.xml',
        'report/reservation_report.xml',
    ],
    'installable': True,
    'application': True,
}