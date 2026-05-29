# -*- coding: utf-8 -*-
from . import controllers
from . import models

# -*- coding: utf-8 -*-
from . import controllers
from . import models

def post_init_hook(env):
    website = env['website'].search([], limit=1)
    if not website:
        return
    company = env['res.company'].search([], limit=1)
    if company:
        company.write({
            'name': 'Exocoms Group',
            'email': 'contact@exocoms.fr',
            'phone': '+33 (0)1 84 79 37 55',
            'country_id': env.ref('base.fr').id,
        })
    website.write({
        'name': 'Exocoms Group',
        'social_facebook': 'https://www.facebook.com/exocoms',
        'social_twitter': 'https://twitter.com/exocoms',
        'social_linkedin': 'https://www.linkedin.com/company/exocoms',
    })
