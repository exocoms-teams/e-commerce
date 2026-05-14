{
    'name': 'Travel Agency',
    'version': '1.0',
    'summary': 'Module Agence de Voyage',
    'description': 'Gestion des voyages, destinations et réservations',
    'category': 'Travel',
    'author': 'Exocoms',
    'depends': ['base', 'product', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/travel_product_views.xml',
        'views/travel_reservation_views.xml',
    ],
    'installable': True,
    'application': True,
}