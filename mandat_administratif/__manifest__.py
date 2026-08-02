# -*- coding: utf-8 -*-
{
    'name': "Mandat administratif (Chorus Pro)",
    'version': '19.0.1.4.0',
    'category': 'Accounting/Payment Providers',
    'summary': "Paiement par mandat administratif pour les entités publiques françaises — dépôt des factures sur Chorus Pro",
    'description': "Module de paiement par mandat administratif pour les entités publiques françaises. Intégration Chorus Pro, SIRET, engagement juridique, PDF de facture et snippet Website Builder.",
    'author': "EXOCOMS Group",
    'website': "https://www.exocoms.fr",
    'license': 'LGPL-3',
    'depends': [
        'payment',
        'account',
        'account_edi_ubl_cii',
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
        'views/res_config_settings_views.xml',
        'views/report_invoice.xml',
        # Snippet website
        'views/snippets/s_mandat_administratif.xml',
        'views/snippets/snippets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mandat_administratif/static/src/ribbon.scss',
        ],
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
