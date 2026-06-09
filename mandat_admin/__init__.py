# -*- coding: utf-8 -*-
from . import models
from . import wizard


def post_init_hook(env):
    # Cherche le compte 512
    account = env['account.account'].search([
        ('code', 'like', '512%'),
        ('company_ids', 'in', env.company.id),
    ], limit=1)

    if not account:
        return  # plan comptable pas encore chargé

    # Vérifie si le journal existe déjà
    journal = env['account.journal'].search([('code', '=', 'MAND')], limit=1)
    if not journal:
        env['account.journal'].create({
            'name': 'Mandat Administratif',
            'code': 'MAND',
            'type': 'bank',
            'sequence': 99,
            'color': 10,
            'default_account_id': account.id,
        })
