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
        'views/partials/dashbord.xml',

        # TEMPLATES
        'views/templates/header.xml',
        'views/templates/footer.xml',
        'views/templates/features.xml',
        'views/templates/layout.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # CSS - DESIGN SYSTEM & CORE
            'exocoms_theme/static/src/css/layout.css',
            # CSS - COMPONENTS
            'exocoms_theme/static/src/css/header.css',
            'exocoms_theme/static/src/css/hero.css',
            'exocoms_theme/static/src/css/features.css',
            'exocoms_theme/static/src/css/products.css',
            'exocoms_theme/static/src/css/footer.css',
            'exocoms_theme/static/src/css/categories.css',
            'exocoms_theme/static/src/css/cta.css',
            'exocoms_theme/static/src/css/dashbord.css',
            # CSS - ANIMATIONS & UTILITIES
            'exocoms_theme/static/src/css/home.css',
            'exocoms_theme/static/src/css/animations.css',
            'exocoms_theme/static/src/css/benefits.css',
            # JS
            'exocoms_theme/static/src/js/main.js',
        ],
    },

    'installable': True,

    'application': True,
}