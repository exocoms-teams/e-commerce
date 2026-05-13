{
    'name': 'Exocoms Theme',
    'version': '1.0',
    'summary': 'Custom website theme for Exocoms Group',
    'author': 'Exocoms Group',
    'license': 'LGPL-3',
    'category': 'Website',
    'depends': [
        'website','website_sale'
    ],
    'data': [
        #DATA
        'data/website_data.xml',
        # PAGES
        'views/pages/home.xml',
        # PARTIALS
        'views/partials/hero.xml',
        'views/partials/portal.xml',
        # TEMPLATES
        'views/templates/header.xml',
        'views/templates/footer.xml',
        'views/templates/features.xml',
        'views/templates/layout.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # CSS
            'exocoms_theme/static/src/css/layout.css',
            'exocoms_theme/static/src/css/header.css',
            'exocoms_theme/static/src/css/hero.css',
            'exocoms_theme/static/src/css/footer.css',
            'exocoms_theme/static/src/css/features.css',
            # JS
            'exocoms_theme/static/src/js/main.js',
        ],
    },

    'installable': True,

    'application': True,
}