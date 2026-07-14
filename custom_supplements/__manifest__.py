{
   'name': 'Boutique Compléments Alimentaires',
    'author': 'Yassine Tartor',
    'license': 'LGPL-3',
    'version': '1.0',
    'summary': 'Vente de protéines, vitamines et gestion des stocks',
    'category': 'eCommerce',
    'depends': [
        'base',
        'website_sale',
        'stock',
        'product_expiry', # Ajout du module de gestion des DLC/DLUO
    ],
    'data': [
        'views/product_template_views.xml',
        'views/website_sale_templates.xml', # Ajout du template Frontend
    ],
    'installable': True,
    'application': True,
}