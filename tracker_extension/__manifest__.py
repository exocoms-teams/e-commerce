{
    'name': 'Tracker Extension Module',
    'version': '2.1.0',
    'category': 'Website',
    'summary': 'Extension download page with dashboard',
    'description': 'Tracker Extension with dark mode, multi-language support, and dashboard',
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['website', 'mail'],
    'data': [
        'views/templates.xml',
        'views/website_menu.xml',
        'views/dashboard_template.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_frontend': [
            'tracker_extension/static/src/css/extension_style.css',
            'tracker_extension/static/src/js/extension_dashboard.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}