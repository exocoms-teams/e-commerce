# -*- coding: utf-8 -*-
{
    'name': 'Contrat Monétique CB',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Page contrat commerçant monétique carte bancaire à 0,25 %',
    'description': 'Landing page du contrat monétique CB EXOCOMS : taux unique, terminal inclus, simulateur d\'économies.',
    'author': 'Exocoms',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale'],
    'data': [
        'views/contrat_monetique_cb_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'contrat_monetique_cb/static/src/css/contrat_monetique_cb.css',
            'contrat_monetique_cb/static/src/js/main.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'auto_install': False,
    'application': False,
}
