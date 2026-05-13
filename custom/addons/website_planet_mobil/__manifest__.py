{

    'name': 'Website Planet Mobil',

    'version': '1.0',

    'author': 'Laeticia Bamba',

    'category': 'Website',

    'summary': 'Module du site Planet Mobil',

    'depends': ['website', 'website_sale'],

    'data': [

        'views/templates.xml',

    ],

    'assets': {

        'web.assets_frontend': [

            'website_planet_mobil/static/src/css/style.css',

        ],

    },

    'installable': True,

    'application': False,

}