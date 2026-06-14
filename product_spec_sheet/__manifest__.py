{
    'name': "Caractéristiques produit",
    'version': '19.0.1.0.0',
    'summary': "Fiches de caractéristiques techniques structurées pour les produits, affichées sur la fiche produit et sur le site e-commerce.",
    'description': """
Caractéristiques produit
=========================

Ce module ajoute :

* des catégories de caractéristiques (ex: Connectivité, Écran, Alimentation, Dimensions et poids)
* des caractéristiques réutilisables, classées par catégorie (ex: Réseaux, Batterie, Encombrement)
* un onglet "Caractéristiques" sur la fiche produit (vue formulaire) pour saisir les valeurs
* un tableau de caractéristiques techniques affiché automatiquement sur la fiche produit du site e-commerce, groupé par catégorie
* un export PDF "Fiche technique" par produit
* un assistant d'import en masse de caractéristiques (coller du texte au format Catégorie ; Caractéristique ; Valeur)
* une page de comparaison des caractéristiques entre plusieurs produits sur le site
""",
    'category': 'Sales/Sales',
    'author': "EXOCOMS Group",
    'license': 'LGPL-3',
    'depends': ['product', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_spec_data.xml',
        'views/product_spec_views.xml',
        'views/product_template_views.xml',
        'views/product_template_templates.xml',
        'views/product_spec_compare_templates.xml',
        'report/product_spec_report_templates.xml',
        'wizard/product_spec_import_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
