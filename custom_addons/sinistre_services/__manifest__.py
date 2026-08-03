# -*- coding: utf-8 -*-
{
    'name': 'Sinistre Services',
    'version': '19.0.2.7.5',
    'category': 'Services',
    'summary': 'Gestion des interventions sinistres — assurances, particuliers, entreprises',
    'author': 'exocoms',
    'website': '',
    'license': 'LGPL-3',
    'post_init_hook':    'post_install_hook',
    'post_migrate_hook': 'post_install_hook',
    'uninstall_hook': 'uninstall_hook',
    'depends': [
        'base', 'mail', 'account', 'sale', 'hr',
        'contacts', 'web', 'website', 'portal',
        'monetique_theme',
        # Dépendances pour débloquer les blocs du website builder
        'website_sale',       # Blocs Catalog + blocs de base (Odoo 17+)
        'website_blog',       # Blocs Blogs
        'appointment',        # Blocs Appointments
        'event',              # Blocs Events
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/document_artisan_access.xml',
        # Data
        'data/init_data.xml',
        'data/sequence_data.xml',
        'data/mission_type_data.xml',
        'data/website_data.xml',
        # Website
        'views/website_homepage.xml',
        'views/website_homepage_inherit.xml',
        'views/website_seo.xml',
        'views/page_intervenant_login.xml',
        'views/website_pages.xml',
        'views/website_prix.xml',
        # Wizards (avant mission_views — références action_sinistre_*_wizard)
        'wizard/assigner_mission_view.xml',
        'wizard/mission_note_wizard_view.xml',
        # Back-office views
        'views/mission_views.xml',
        'views/intervenant_views.xml',
        'views/candidature_views.xml',
        'views/assurance_views.xml',
        'views/devis_views.xml',
        'views/page_suivi.xml',
        'views/menu_views.xml',
        # Reports
        'report/report_mission.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'monetique_theme/static/src/css/main.css',
            'sinistre_services/static/src/css/prix.css',
        ],
        'web.assets_backend': [
            'sinistre_services/static/src/css/backend.css',
        ],
    },
    'installable': True,
    'test': ['tests/test_sinistre.py'],
    'application': True,
    'auto_install': False,
}
