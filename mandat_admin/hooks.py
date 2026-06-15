# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Crée le journal 'Mandats Administratifs' et y rattache
    la méthode de paiement mandat_administratif à l'installation.
    """
    PaymentMethod = env['account.payment.method']
    Journal = env['account.journal']
    company = env.company

    provider = env['payment.provider'].search([
        ('code', '=', 'mandat_administratif')
    ], limit=1)
    if not provider:
        env['payment.provider'].create({
            'name': 'Mandat Administratif',
            'code': 'mandat_administratif',
            'state': 'enabled',
            'is_published': True,
        })

    # Récupère la méthode de paiement créée par payment_method_data.xml
    method = PaymentMethod.search([('code', '=', 'mandat_administratif')], limit=1)
    if not method:
        _logger.warning('mandat_admin: méthode de paiement introuvable, hook ignoré.')
        return

    # Vérifie si le journal existe déjà (idempotent)
    journal = Journal.search([
        ('code', '=', 'MA'),
        ('company_id', '=', company.id),
    ], limit=1)

    if not journal:
        journal = Journal.create({
            'name': 'Mandats Administratifs',
            'code': 'MA',
            'type': 'bank',
            'company_id': company.id,
        })
        _logger.info('mandat_admin: journal "Mandats Administratifs" créé (id=%d)', journal.id)
    else:
        _logger.info('mandat_admin: journal MA déjà existant, rattachement de la méthode.')

    # Rattache la méthode au journal si pas déjà présente
    existing = journal.outbound_payment_method_line_ids.mapped(
        'payment_method_id'
    )
    if method not in existing:
        env['account.payment.method.line'].create({
            'payment_method_id': method.id,
            'journal_id': journal.id,
        })
        _logger.info('mandat_admin: méthode "Mandat Administratif" rattachée au journal MA.')