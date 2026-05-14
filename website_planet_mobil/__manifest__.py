
{
    'name': 'Planet Mobil - eCommerce',
    'version': '1.0',
    'category': 'Website/eCommerce',
    'summary': 'Site eCommerce Planet Mobil - Produits Apple',
    'description': 'Module personnalise pour le site Planet Mobil',
    'author': 'EXOCOMS Group',
    'website': 'https://www.planet-mobil.com',
    'depends': [
        'website',
        'website_sale',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'templates/header.xml',
        'templates/footer.xml',
        'templates/homepage.xml',
        'templates/category_page.xml',
        'templates/product_page.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
            'website_planet_mobil/static/src/css/style.css',
            'website_planet_mobil/static/src/js/main.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}