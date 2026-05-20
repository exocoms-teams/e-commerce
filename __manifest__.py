# -*- coding: utf-8 -*-
{
    'name': 'Mandat Administratif France',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment',
    'summary': 'Gestion des mandats administratifs pour les marchés publics français',
    'description': """
        Module de gestion des mandats administratifs conformément
        à la réglementation française (décret n° 2016-360 relatif aux marchés publics).
        
        Fonctionnalités :
        - Création et suivi des mandats administratifs
        - Workflow de validation (liquidation → ordonnancement → paiement)
        - Lien avec les bons de commande et factures
        - Génération du bordereau des mandats
        - Gestion du budget et des engagements
        - Rapports réglementaires
        - Conformité avec la comptabilité publique française (M57, M14...)
    """,
    'author': 'Votre Organisation',
    'website': 'https://www.votre-site.fr',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'purchase',
        'mail',
        'document',
    ],
    'data': [
        'security/mandat_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/mandat_data.xml',
        'views/mandat_administratif_views.xml',
        'views/bordereau_mandat_views.xml',
        'views/engagement_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
        'wizard/wizard_valider_mandat_views.xml',
        'report/report_mandat_administratif.xml',
        'report/report_bordereau_mandats.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}
