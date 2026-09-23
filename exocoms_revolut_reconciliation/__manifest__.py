# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.
{
    'name': "Revolut Business : rapprochement bancaire",
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': "Importe les transactions Revolut Business dans les relevés bancaires Odoo.",
    'description': " ",
    'author': "EXOCOMS Group",
    'website': "https://www.exocoms.fr",
    'license': 'OPL-1',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/revolut_business_connection_views.xml',
        'views/account_journal_views.xml',
        'data/ir_cron_data.xml',
    ],
}
