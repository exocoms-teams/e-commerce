# -*- coding: utf-8 -*-
{
    'name': "Mandat administratif (Chorus Pro)",
    'version': '19.0.1.3.0',
    'category': 'Accounting/Payment Providers',
    'summary': "Paiement par mandat administratif pour les entités publiques françaises — dépôt des factures sur Chorus Pro",
    'description': """
Mandat administratif — Chorus Pro
=================================
Module de paiement destiné aux administrations, collectivités territoriales
et établissements publics français.

Fonctionnalités
---------------
* Fournisseur de paiement « Mandat administratif » (flux différé, transaction
  mise en attente comme le virement bancaire).
* Visible au checkout eCommerce uniquement pour les partenaires marqués
  « Entité publique ».
* Champs Chorus Pro sur le partenaire : SIRET destinataire (contrôle de la
  clé de Luhn), code service, engagement juridique obligatoire.
* Report des informations sur le devis / bon de commande et la facture :
  n° d'engagement juridique, code service.
* Bloc « Règlement par mandat administratif — Chorus Pro » ajouté au PDF
  de facture.
* Suivi du dépôt sur Chorus Pro depuis la facture (bouton « Déposée sur
  Chorus Pro » + horodatage) et lien direct vers le portail.
* Snippet Website Builder « Mandat administratif » prêt à glisser-déposer
  sur le site.

Cadre réglementaire : facturation électronique obligatoire via Chorus Pro
(ordonnance n° 2014-697, décret n° 2016-1478) — délai global de paiement
de 30 jours (Code de la commande publique).

Compatibilité : Odoo 19 (Odoo.sh) uniquement — non compatible avec les
versions antérieures.
    """,
    'author': "EXOCOMS Group",
    'website': "https://www.exocoms.fr",
    'license': 'LGPL-3',
    'depends': [
        'payment',
        'account',
        'sale_management',
        'website_sale',
    ],
    'data': [
        # Templates de paiement d'abord (référencés par les données du provider)
        'views/payment_form_templates.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        # Vues backend
        'views/payment_provider_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        # Snippet website
        'views/snippets/s_mandat_administratif.xml',
        'views/snippets/snippets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'mandat_administratif/static/src/snippets/s_mandat_administratif/000.scss',
            'mandat_administratif/static/src/payment_badge.scss',
            'mandat_administratif/static/src/interactions/payment_badge.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
}
