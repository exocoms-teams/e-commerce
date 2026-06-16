{
    'name': 'EXOCOMS – Filtre Sidebar Modèle D',
    'version': '19.0.1.0.0',
    'summary': 'Sidebar filtre 3 niveaux : service → sous-catégorie → item, slider prix double, AJAX auto',
    'description': """
        Sidebar de filtres produits Modèle D pour Odoo 19 Website / eCommerce.
        • Menu accordéon 3 niveaux (service → sous-catégorie → item)
        • Icônes colorées par domaine métier EXOCOMS
        • Slider double curseur pour le filtre prix (bornes dynamiques depuis le catalogue)
        • Rafraîchissement automatique AJAX (debounce 300 ms)
        • Tags filtres actifs supprimables individuellement
        • Pagination AJAX, URL partageable (pushState)
        • Version module intégré ET snippet Website Builder drag & drop
        • Miniature SVG + options panneau Website Builder
    """,
    'author': 'EXOCOMS Group',
    'website': 'https://www.exocoms.fr',
    'category': 'Website/eCommerce',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/snippet_options.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'exocoms_filter_menu/static/src/css/sidebar.css',
            'exocoms_filter_menu/static/src/js/sidebar.js',
        ],
        'website.assets_wysiwyg': [
            'exocoms_filter_menu/static/src/js/snippet_editor.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
