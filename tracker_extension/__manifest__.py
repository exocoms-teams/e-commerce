{
    'name': 'Tracker Extension Module',
    'version': '2.1.0',
    'category': 'Website',
    'summary': 'Extension download page with dashboard',
    'description': """Tracker Extension with dark mode, multi-language support ,
     Ce module permet de :
        - Capturer les données de produits via l'extension navigateur.
        - Analyser les scores de tendances (Winning Products).
        - Fournir un tableau de bord d'aide à la décision pour les e-commerçants.""",
    'author': 'Exocoms Group',
    'website': 'https://www.exocoms.fr',
    'license': 'LGPL-3',
    'depends': ['website', 'mail'],
    'data': [
        'views/home_template.xml',
        'views/templates.xml',
        'views/website_menu.xml',
        'views/dashboard_template.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_frontend': [
            'tracker_extension/static/css/extension_style.css',
            'tracker_extension/static/js/extension_dashboard.js',
            'tracker_extension/static/js/homepage.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}