{
    'name': 'Monetique - Fiche Technique Produits',
    'version': '1.0',
    'summary': "Champs métier monétique (TPE, bornes, connectivité, certifications) "
               "sur les fiches produit et la fiche vendeur du site.",
    'description': """
Module R&D "Monétique" — Exocoms Group France
==============================================

Ajoute au catalogue (product.template) les informations spécifiques au métier
de la monétique, absentes du module e-commerce standard et du module
Multi Vendor Marketplace :

- Catégorie monétique (TPE fixe / portable / mobile / borne libre-service / accessoire)
- Certification PCI-DSS
- Type de connectivité (Wifi / 4G / Ethernet / Bluetooth / Sans contact)
- Autonomie de la batterie (heures)
- Durée de garantie (mois)
- Référence constructeur / modèle certifié banque

Ces champs sont exposés :
1. Côté back-office : nouvel onglet "Fiche Monétique" sur la fiche produit.
2. Côté site web : bloc "Fiche technique" sur la page produit (/shop) et
   badges sur les cartes produit du thème monetique_theme.
""",
    'author': 'Exocoms Group France',
    'license': 'LGPL-3',
    'category': 'Website/eCommerce',
    'depends': ['product', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/product_page_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'monetique_specs/static/src/css/specs.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
