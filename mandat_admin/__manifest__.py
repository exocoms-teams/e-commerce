# -*- coding: utf-8 -*-
{
    'name': 'Mandat Administratif (Chorus Pro)',
    'version': '19.0.4.0.0',
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
  « Organisme public ».
* Wizard BCA complet : SIRET (contrôle Luhn), IBAN, imputation budgétaire,
  pièces justificatives, PDF BCA conforme GBCP, envoi email automatique.
* Workflow mandat : service fait certifié, prise en charge comptable (PEC),
  bordereau récapitulatif signé par l'ordonnateur.
* Export XML UBL 2.1 / Factur-X pour dépôt sur Chorus Pro.
* Suivi du dépôt sur Chorus Pro depuis la facture (bouton « Déposée sur
  Chorus Pro » + horodatage) et lien direct vers le portail.
* Bloc « Règlement par mandat administratif — Chorus Pro » ajouté au PDF
  de facture.
* Calcul automatique des intérêts moratoires et gestion TVA publique (FCTVA).
* Snippet Website Builder « Mandat administratif » prêt à glisser-déposer
  sur le site.

Cadre réglementaire : facturation électronique obligatoire via Chorus Pro
(ordonnance n° 2014-697, décret n° 2016-1478) — délai global de paiement
de 30 jours (Code de la commande publique).

Compatibilité : Odoo 19 (Odoo.sh) uniquement — non compatible avec les
versions antérieures.
    """,
    'author': 'EXOCOMS Group',
    'website': 'https://www.exocoms.fr',
    'license': 'LGPL-3',
    'depends': ['account', 'sale', 'sale_management', 'mail', 'payment', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/payment_method_data.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/mandat_bordereau_views.xml',
        'views/menus.xml',
        'wizard/mandat_wizard_views.xml',
        'wizard/service_fait_wizard_views.xml',
        'wizard/pec_wizard_views.xml',
        'wizard/bordereau_wizard_views.xml',
        'report/report_action.xml',
        'report/bca_template.xml',
        'report/bordereau_template.xml',
        'views/report_invoice.xml',
        'views/mandat_redirect_form.xml',
        'views/mandat_inline_form.xml',
        'data/payment_provider_data.xml',
        'views/mandat_checkout_template.xml',
        'views/mandat_confirmation_page.xml',
        'views/snippets/s_mandat_administratif.xml',
        'views/snippets/snippets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mandat_admin/static/src/css/mandat.css',
        ],
        'web.assets_frontend': [
            'mandat_admin/static/src/css/mandat_payment.css',
            'mandat_admin/static/src/js/mandat_checkout.js',
            'mandat_admin/static/src/js/mandat_post_processing.js',
            'mandat_admin/static/src/snippets/s_mandat_administratif/000.scss',
            'mandat_admin/static/src/payment_badge.scss',
            'mandat_admin/static/src/interactions/payment_badge.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
