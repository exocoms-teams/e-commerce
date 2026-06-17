# -*- coding: utf-8 -*-
from . import models
from . import wizard
from . import controllers

def post_init_hook(env):
    if env['account.journal'].search([('code', '=', 'MAND')], limit=1):
        return
    account = env['account.account'].search([
        ('account_type', '=', 'asset_cash'),
    ], limit=1)
    if not account:
        return
    env['account.journal'].create({
        'name': 'Mandat Administratif',
        'code': 'MAND',
        'type': 'bank',
        'sequence': 99,
        'color': 10,
        'default_account_id': account.id,
    })
