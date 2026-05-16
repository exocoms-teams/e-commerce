# -*- coding: utf-8 -*-
{
    'name': 'Sinistre Services',
    'version': '19.0.2.0.0',
    'category': 'Website/Services',
    'summary': 'Gestion des interventions sinistres — assurances, particuliers, entreprises',
    'description': """
        Plateforme complète de gestion des sinistres et interventions :
        • Réception des ordres de mission des assurances via API REST (clé API)
        • Formulaire de demande directe particuliers / entreprises (sans assurance)
        • Dispatch des intervenants artisans (serruriers, plombiers, menuisiers…)
        • Gestion devis, photos avant/après, facturation, commissions
        • Site web public avec design system (Poppins + bleu #0D47A1)
        • Suivi dossier par token public
        • Modal urgence + formulaire de rappel
    """,
    'author': 'exocoms',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'account',
        'sale',
        'project',
        'hr',
        'contacts',
        'web',
        'website',
        'portal',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/sequence_data.xml',
        'data/mission_type_data.xml',
        'data/website_data.xml',
        # Back-office views
        'views/mission_views.xml',
        'views/intervenant_views.xml',
        'views/assurance_views.xml',
        'views/devis_views.xml',
        'views/menu_views.xml',
        # Website (front)
        'views/website_layout.xml',
        'views/website_homepage.xml',
        'views/website_pages.xml',
        # Reports
        'report/report_mission.xml',
        # Wizards
        'wizard/assigner_mission_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'sinistre_services/static/src/css/variables.css',
            'sinistre_services/static/src/css/base.css',
            'sinistre_services/static/src/css/layout.css',
            'sinistre_services/static/src/css/homepage.css',
            'sinistre_services/static/src/css/pages.css',
            'sinistre_services/static/src/js/main.js',
        ],
        'web.assets_backend': [
            'sinistre_services/static/src/css/backend.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
