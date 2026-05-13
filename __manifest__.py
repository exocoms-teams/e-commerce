# -*- coding: utf-8 -*-
{
    'name': 'Sinistre Services - Gestion des Interventions',
    'version': '19.0.1.0.0',
    'category': 'Services',
    'summary': 'Gestion des ordres de mission sinistres (assurances, particuliers, entreprises)',
    'description': """
        Module de gestion des interventions sinistres :
        - Réception des ordres de mission des assurances via API
        - Demandes directes particuliers et professionnels
        - Gestion des intervenants (serruriers, plombiers, menuisiers...)
        - Devis, facturation assurance + reste à charge
        - Commissions intervenants
        - Suivi photo et clôture de dossier
    """,
    'author': 'exocoms',
    'website': 'https://exocoms.fr',
    'depends': [
        'base',
        'mail',
        'account',
        'sale',
        'project',
        'hr',
        'contacts',
        'web',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/sequence_data.xml',
        'data/mission_type_data.xml',
        # Views
        'views/mission_views.xml',
        'views/intervenant_views.xml',
        'views/assurance_views.xml',
        'views/devis_views.xml',
        'views/menu_views.xml',
        # Reports
        'report/report_mission.xml',
        'report/report_facture_assurance.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'monetique_theme/static/src/css/variables.css',
            'monetique_theme/static/src/css/base.css',
            'monetique_theme/static/src/css/layout.css',
            'monetique_theme/static/src/css/homepage.css',
            'monetique_theme/static/src/css/pages.css',
            'monetique_theme/static/src/css/shop.css',
            'monetique_theme/static/src/js/main.js',
        ],
        'web.assets_backend': [
            'sinistre_services/static/src/css/sinistre.css',
            'sinistre_services/static/src/js/mission_kanban.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
