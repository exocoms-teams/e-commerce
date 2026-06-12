# -*- coding: utf-8 -*-
{
    'name': 'Mandat Administratif',
    'version': '19.0.4.0.0',
    'category': 'Accounting/Payment',
    'summary': 'Gestion complète des mandats administratifs conformes GBCP pour organismes publics français',
    'description': """
Mandat Administratif Français – Conforme GBCP
==============================================

Références réglementaires
--------------------------

- Décret n°2012-1246 du 7 novembre 2012 (GBCP)
- Décret n°2016-33 du 20 janvier 2016 (pièces justificatives)
- Article L.1617-1 CGCT (comptabilité publique)
- Article L.2192-10 CCP (délai 30 jours, intérêts moratoires)
- Arrêté du 9 décembre 2016 (Chorus Pro)
- Nomenclatures M14 / M57 / M22

Fonctionnalités
---------------

- Sélection "Mandat Administratif" au moment du paiement (account.payment)
- Wizard BCA complet : SIRET Luhn, IBAN, imputation budgétaire, PJ
- Certification du service fait (obligatoire)
- Prise en charge comptable (PEC)
- Export XML UBL 2.1 / Factur-X pour Chorus Pro
- Bordereau récapitulatif des mandats signé par l'ordonnateur
- Calcul automatique des intérêts moratoires
- Gestion TVA publique (FCTVA, assujetti partiel)
- PDF BCA conforme GBCP avec zones de signature
    """,
    'author': 'Exocoms',
    'website': 'https://www.exocoms.fr',
    'license': 'LGPL-3',
    'depends': ['account', 'sale', 'sale_management', 'mail'],
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
    ],
    'assets': {
        'web.assets_backend': [
            'mandat_admin/static/src/css/mandat.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
