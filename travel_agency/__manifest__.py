{
    'name': 'Travel Agency',
    'version': '1.0',
    'author': 'ARMOD07',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/travel_reservation_views.xml',
        'views/travel_product_views.xml',
    ],
    'installable': True,
    'application': True,
}