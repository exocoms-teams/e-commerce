{
    'name': 'Tracker Extension Download',
    'version': '2.1.0',
    'category': 'Website',
    'license': 'LGPL-3',
    'summary': 'Download the Tracker browser extension',
    'description': """
        Provides the Tracker browser extension for download.
        Track products automatically on e-commerce sites.
        
        Features:
        - Auto-detection on Amazon, eBay, Etsy, Walmart
        - Local data storage (no cloud sync)
        - Full dashboard with charts
        - CSV export functionality
    """,
    'author': 'Your Company',
    'website': 'https://your-company.com',
    'depends': ['website'],
    'data': [
        'views/templates.xml',
        'views/website_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}