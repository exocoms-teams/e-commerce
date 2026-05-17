# -*- coding: utf-8 -*-
{
    'name': 'Sinistre Services',
    'version': '19.0.2.0.0',
    'category': 'Services',
    'summary': 'Gestion des interventions sinistres — assurances, particuliers, entreprises',
    'author': 'exocoms',
    'website': '',
    'license': 'LGPL-3',
    'post_init_hook': 'post_install_hook',
    'uninstall_hook': 'uninstall_hook',
    'depends': [
    'base', 'mail', 'account', 'sale', 'hr',
    'contacts', 'web', 'website', 'portal',
    'monetique_theme',   # ← ajouter
    ],
   'data': [
    # Security
    'security/security.xml',
    'security/ir.model.access.csv',
    # Data
    'data/init_data.xml',
    'data/sequence_data.xml',
    'data/mission_type_data.xml',
    'data/website_data.xml',
    # Website
    # Website
    'views/website_homepage.xml',
    'views/website_layout.xml',
       
    # Back-office views
    'views/mission_views.xml',
    'views/intervenant_views.xml',
    'views/assurance_views.xml',
    'views/devis_views.xml',
    'views/menu_views.xml',
    # Reports
    'report/report_mission.xml',
    # Wizards
    'wizard/assigner_mission_view.xml',
],
'assets': {
    'web.assets_frontend': [],
    'web.assets_backend': [
        'sinistre_services/static/src/css/backend.css',
    ],
},
    'installable': True,
    'application': True,
    'auto_install': False,
}
