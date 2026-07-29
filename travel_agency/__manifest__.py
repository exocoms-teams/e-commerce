{
    'name': 'Travel Agency',
    'version': '1.0',
    'author': 'ARMOD07',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': ['base', 'product', 'website', 'website_sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/email_template.xml',
        'data/demo.xml',
        
        # Vues existantes
        'views/travel_dashboard.xml',
        'views/travel_product_views.xml',
        'views/travel_reservation_views.xml',
        'views/travel_hotel_views.xml',
        'views/travel_vol_views.xml',
        'views/travel_train_views.xml',
        'views/travel_car_views.xml',
        
        # NOUVEAUX MODULES - Vues backoffice
        'views/travel_guide_views.xml',      # Guide touristique
        'views/travel_leisure_views.xml',    # Sorties & Loisirs
        'views/travel_rental_views.xml',     # Location de maison
        
        # Vues existantes
        'views/payment_provider_views.xml',
        
        # Vues website existantes
        'views/website_travel.xml',
        'views/website_hotel.xml',
        'views/website_vol.xml',
        'views/website_train.xml',
        'views/website_car.xml',
        
        # NOUVEAUX MODULES - Vues website
        'views/website_guide.xml',           # Website guide
        # 'views/website_leisure.xml',       # TODO: fichier manquant - a creer (templates travel_agency.website_leisure_list/detail attendus par controllers/main.py)
        # 'views/website_rental.xml',        # TODO: fichier manquant - a creer (templates travel_agency.website_rental_list/detail attendus par controllers/main.py)
        
        # Menu et rapports
        'views/website_menu.xml',
        'report/reservation_report.xml',
    ],
    'installable': True,
    'application': True,
}