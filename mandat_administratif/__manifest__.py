# -*- coding: utf-8 -*-
{
    'name': "Mandat administratif (Chorus Pro)",
    'version': '19.0.2.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': "Paiement par mandat administratif pour les entités publiques françaises — dépôt des factures sur Chorus Pro",
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
- Nomenclatures M14 / M57 / M22 / M52 / M71

Fonctionnalités
---------------
- Mode de paiement "Mandat Administratif" au checkout eCommerce (entités publiques uniquement)
- Formulaire SIRET / ordonnateur / comptable intégré au checkout
- Wizard BCA complet : imputation budgétaire, pièces justificatives, IBAN fournisseur
- Workflow : BCA → Service fait → PEC → Mandatement → Payé
- Export XML UBL 2.1 / Factur-X compatible Chorus Pro
- Email automatique du BCA à la validation
- Boutons de suivi dépôt Chorus Pro sur la facture
- Snippet Website Builder "Mandat administratif"
- Calcul automatique des intérêts moratoires
- Gestion TVA publique (FCTVA, assujetti partiel)
- PDF BCA conforme GBCP avec zones de signature
    """,
    'author': "EXOCOMS Group",
    'website': "https://www.exocoms.fr",
    'license': 'LGPL-3',
    'depends': [
        'payment',
        'account',
        'sale_management',
        'website_sale',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_form_templates.xml',
        'data/payment_provider_data.xml',
        'data/payment_method_data.xml',
        'data/sequence_data.xml',
        'views/payment_provider_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/menus.xml',
        'views/account_move_views.xml',
        'views/mandat_confirmation_page.xml',
        'views/snippets/s_mandat_administratif.xml',
        'views/snippets/snippets.xml',
        'report/report_action.xml',
        'report/bca_template.xml',
        'wizard/mandat_wizard_views.xml',
        'wizard/service_fait_wizard_views.xml',
        'wizard/pec_wizard_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'mandat_administratif/static/src/snippets/s_mandat_administratif/000.scss',
            'mandat_administratif/static/src/payment_badge.scss',
            'mandat_administratif/static/src/interactions/payment_badge.js',
        ],
        'payment.assets_payment_form_content': [
            'mandat_administratif/static/src/js/mandat_checkout.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
}
