{
    'name': 'Tracker Extension Module',
    'version': '2.1.0',
    'category': 'Website',
    'summary': 'Extension download page with dashboard',
    'description': """
        Tracker Extension with:
        - Green/White theme with dark mode toggle
        - French/English language support
        - Dashboard for extension data
    """,
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'depends': ['website', 'mail'],
    'data': [
        'views/templates.xml',
        'views/website_menu.xml',
        'views/dashboard_template.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_frontend': [
            'your_module_name/static/css/extension_style.css',
            'your_module_name/static/js/extension_dashboard.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}