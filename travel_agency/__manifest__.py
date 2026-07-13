{
    'name': 'Travel Agency',
    'version': '1.0',
    'author': 'ARMOD07',
    'license': 'LGPL-3',
    'category': 'Sales',
    'description': 'Gestion des reservations pour agence de voyage.',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/travel_reservation_views.xml',
        'views/travel_product_views.xml',
        'views/payment_provider_views.xml',
        'report/reservation_report.xml',
        'payment_module/views/payment_transaction_views.xml',
    ],
    'installable': True,
    'application': True,
}

#AMIRA