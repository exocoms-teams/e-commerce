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
    ],
    'installable': True,
    'application': True,
}