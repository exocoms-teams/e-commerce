{
    'name': 'Tracker Extension Download',
    'version': '2.1.0',
    'category': 'Website',
    'summary': 'Download the Tracker browser extension',
    'description': """
        Provides the Tracker browser extension for download.
        Track products automatically on e-commerce sites.
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