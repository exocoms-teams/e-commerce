# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
{
    'name': 'LUMIÈRE Beauty Core',
    'version': '1.0',
    'category': 'Website/E-commerce',
    'summary': 'Gestion personnalisée des fiches cosmétiques pour LUMIÈRE Beauty',
    'description': """Ce module ajoute des champs personnalisés pour la marque LUMIÈRE :
- Type de cosmétique
- Finition (Mat, Prismatic Glow, Gloss...)
- Ingrédients clés (Beurre de karité, Vitamine E...)
- Gestion des teintes et des recommandations de peau.""",
    'author': 'Maram Hadj Ali',
    'depends': ['website_sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/lumiere_beauty/static/src/css/lumiere_style.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}