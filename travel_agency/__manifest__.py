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
        
    
        'views/travel_dashboard.xml',
        'views/travel_product_views.xml',
        'views/travel_reservation_views.xml',
        'views/travel_hotel_views.xml',
        'views/travel_vol_views.xml',
        'views/travel_train_views.xml',
        'views/travel_car_views.xml',
        
        'views/travel_guide_views.xml',     
        'views/travel_leisure_views.xml',  
        'views/travel_rental_views.xml',     
        'views/payment_provider_views.xml',
        'views/website_travel.xml',
        'views/website_hotel.xml',
        'views/website_vol.xml',
        'views/website_train.xml',
        'views/website_car.xml',
        'views/website_guide.xml',          
        'views/website_menu.xml',
        'report/reservation_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'travel_agency/static/src/scss/travel_backend.scss',
        ],
    },
    'installable': True,
    'application': True,
}