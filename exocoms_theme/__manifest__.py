{
    'name': 'Exocoms Theme',
    'version': '19.0.1.0.3',
    'summary': 'Custom website theme for Exocoms Group',
    'author': 'Exocoms Group',
    'license': 'LGPL-3',
    'category': 'Website',
    'depends': [
        'website',
        'website_sale',
    ],
    'data': [
        'data/website_data.xml',
        'views/pages/home.xml',
        'views/pages/services.xml',
        'views/pages/mentions_legales.xml',
        'views/pages/boutique.xml',
        'views/partials/hero.xml',
        'views/partials/dashbord.xml',
        'views/partials/dashbord_boutique.xml',
        'views/partials/services_hero.xml',
        'views/partials/services_content.xml',
        'views/partials/mentions_legales_content.xml',
        'views/partials/portal.xml',
        'views/templates/header.xml',
        'views/templates/footer.xml',
        'views/templates/features.xml',
        'views/templates/layout.xml',
        'views/templates/services_features.xml',
        'data/seo_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # ── 1. Fondations : variables, reset, typographie, boutons génériques ──
            'exocoms_theme/static/src/css/layout.css',

            # ── 2. Sections de base (style desktop uniquement, sans @media) ──
            'exocoms_theme/static/src/css/header.css',
            'exocoms_theme/static/src/css/hero.css',
            'exocoms_theme/static/src/css/features.css',
            'exocoms_theme/static/src/css/products.css',
            'exocoms_theme/static/src/css/footer.css',
            'exocoms_theme/static/src/css/categories.css',
            'exocoms_theme/static/src/css/cta.css',
            'exocoms_theme/static/src/css/dashbord.css',
            'exocoms_theme/static/src/css/dashbord_boutique.css',
            'exocoms_theme/static/src/css/services_content.css',
            'exocoms_theme/static/src/css/services_features.css',
            'exocoms_theme/static/src/css/services_hero.css',
            'exocoms_theme/static/src/css/home.css',
            'exocoms_theme/static/src/css/legal.css',
            'exocoms_theme/static/src/css/animations.css',
            'exocoms_theme/static/src/css/benefits.css',
            'exocoms_theme/static/src/css/cards.css',
            'exocoms_theme/static/src/css/pages.css',
            'exocoms_theme/static/src/css/sections.css',
            'exocoms_theme/static/src/css/home_sections.css',
            'exocoms_theme/static/src/css/odoo-integration.css',

            # ── 3. RESPONSIVE — doit TOUJOURS être chargé en dernier ──
            # Contient désormais TOUTES les media queries du thème,
            # fusionnées depuis tous les fichiers ci-dessus.
            'exocoms_theme/static/src/css/responsive.css',

            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
            # JS
            'exocoms_theme/static/src/js/main.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'post_migrate': 'post_migrate_hook',
    'installable': True,
    'application': True,
}