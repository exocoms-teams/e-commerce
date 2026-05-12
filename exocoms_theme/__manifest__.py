{
    'name': 'Exocoms Theme',
    'version': '1.0',
    'category': 'Theme',
    'depends': [
        'website',
    ],
    'data': [
        #DATA
        'data/website_menu.xml',
        # PAGES
        'views/pages/home.xml',
        # PARTIALS
        'views/partials/hero.xml',
        # TEMPLATES
        'views/templates/header.xml',
        'views/templates/footer.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # CSS
            'exocoms_theme/static/src/css/layout.css',
            'exocoms_theme/static/src/css/header.css',
            'exocoms_theme/static/src/css/hero.css',
            'exocoms_theme/static/src/css/footer.css',
            # JS
            'exocoms_theme/static/src/js/main.js',
        ],
    },

    'installable': True,

    'application': True,
}