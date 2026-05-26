{
    'name': 'SerruPro',
    'version': '1.0',
    'category': 'Website',
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
    'static_description_path': 'description',
    'installable': True,
}