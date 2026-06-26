{
    'name': 'SerruPro',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Site pour services de serrurerie',
    'author': 'Exo_coms',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'sale_management',
        'calendar',
        'crm',
        'payment',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'installable': True,
    'application': True,
}