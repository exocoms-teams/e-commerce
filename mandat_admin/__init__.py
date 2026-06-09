# -*- coding: utf-8 -*-
from . import models
from . import wizard


def post_init_hook(env):
    """Assigne un compte de trésorerie au journal MAND après installation."""
    journal = env.ref(
        'mandat_admin.account_journal_mandat_administratif',
        raise_if_not_found=False
    )
    if not journal:
        return

    # Cherche le compte 512 (Banques) dans le plan comptable de la société
    company = env.company
    account = env.ref('l10n_fr.1_pcg_512', raise_if_not_found=False)

    # Fallback : cherche n'importe quel compte 512 lié à la société
    if not account:
        account = env['account.account'].search([
            ('code', 'like', '512%'),
            ('company_ids', 'in', company.id),
        ], limit=1)

    if account and not journal.default_account_id:
        journal.default_account_id = account.id
