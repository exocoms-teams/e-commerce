# -*- coding: utf-8 -*-
{
    'name': 'Mandat Administratif Français',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Gestion des mandats administratifs pour les collectivités et administrations françaises',
    'description': """
Mandat Administratif Français
==============================

Ce module permet de gérer les mandats administratifs conformément à la
réglementation française (Instruction budgétaire et comptable M14, M52, M57).

Fonctionnalités :
-----------------
* Création et gestion des mandats de paiement
* Numérotation automatique conforme aux nomenclatures françaises
* Gestion des bordereaux de mandats
* Suivi des états : Brouillon → Validé → Mandaté → Payé → Annulé
* Pièces justificatives attachées
* Génération de l'ordonnancement de dépense (OD)
* Export comptable compatible Hélios / CHD / GFC
* Gestion des imputations budgétaires (chapitres, articles, rubriques)
* Contrôle de disponibilité des crédits
* Certificat de prise en charge comptable
* Journal de mandatement
* Rapport de synthèse par période

Conformité réglementaire :
--------------------------
* Instruction M14 (communes)
* Instruction M52 (départements)
* Instruction M57 (régions et autres collectivités)
* DGFIP - Direction Générale des Finances Publiques
    """,
    'author': 'Localisation Française',
    'website': 'https://www.collectivites-locales.gouv.fr',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
        'base_setup',
    ],
    'data': [
        # Sécurité
        'security/mandat_security.xml',
        'security/ir.model.access.csv',

        # Données de référence
        'data/mandat_sequence.xml',
        'data/mandat_type_data.xml',
        'data/payment_provider_data.xml',
        'data/account_journal_data.xml',

        # Vues
        'views/mandat_administratif_views.xml',
        'views/bordereau_mandat_views.xml',
        'views/imputation_budgetaire_views.xml',
        'views/payment_mandat_views.xml',
        'views/account_move_mandat_views.xml',
        'views/mandat_menu.xml',

        # Rapports
        'report/mandat_report.xml',
        'report/bordereau_report.xml',

        # Wizard
        'wizard/validation_mandat_wizard_views.xml',
        'wizard/export_helios_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mandat_admin/static/src/css/mandat_style.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'post_migrate_hook': 'post_init_hook',
    'images': ['static/description/icon.png'],
}
