# -*- coding: utf-8 -*-
{
    'name': 'LUMIÈRE Beauty Core',
    'version': '1.0',
    'category': 'Website/E-commerce',
    'summary': 'Gestion personnalisée des fiches cosmétiques pour LUMIÈRE Beauty',
    'author': 'Maram Hadj Ali',
    'depends': ['website_sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    # Configuration des assets pour charger votre CSS sur le Front-End (Site Web)
    'assets': {
        'web.assets_frontend': [
            '/lumiere_beauty/static/src/css/lumiere_style.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}