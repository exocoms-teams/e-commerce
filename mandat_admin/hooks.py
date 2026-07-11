# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Crée (ou récupère) le payment.method et le payment.provider mandat_administratif,
    crée le journal MA et y rattache la méthode.
    Idempotent : peut être appelé plusieurs fois sans effet de bord.
    """
    cr = env.cr

    # --- 1. get-or-create payment.method (évite le conflit d'unicité) ---
    pm = env['payment.method'].search([('code', '=', 'mandat_administratif')], limit=1)
    if not pm:
        pm = env['payment.method'].create({
            'name': 'Mandat Administratif',
            'code': 'mandat_administratif',
        })
        _logger.info('mandat_admin: payment.method créé (id=%d)', pm.id)

    # --- 2. get-or-create payment.provider et lier la méthode ---
    provider = env['payment.provider'].search([('code', '=', 'mandat_administratif')], limit=1)
    if provider and pm not in provider.payment_method_ids:
        provider.write({'payment_method_ids': [(4, pm.id)]})

    # --- 3. get-or-create account.payment.method ---
    apm = env['account.payment.method'].search([('code', '=', 'mandat_administratif')], limit=1)
    if not apm:
        apm = env['account.payment.method'].create({
            'name': 'Mandat Administratif',
            'code': 'mandat_administratif',
            'payment_type': 'outbound',
        })
        _logger.info('mandat_admin: account.payment.method créé (id=%d)', apm.id)

    # --- 4. get-or-create journal MA et rattacher la méthode ---
    company = env.company
    journal = env['account.journal'].search([
        ('code', '=', 'MA'),
        ('company_id', '=', company.id),
    ], limit=1)
    if not journal:
        journal = env['account.journal'].create({
            'name': 'Mandats Administratifs',
            'code': 'MA',
            'type': 'bank',
            'company_id': company.id,
        })
        _logger.info('mandat_admin: journal MA créé (id=%d)', journal.id)

    existing_methods = journal.outbound_payment_method_line_ids.mapped('payment_method_id')
    if apm not in existing_methods:
        env['account.payment.method.line'].create({
            'payment_method_id': apm.id,
            'journal_id': journal.id,
        })
        _logger.info('mandat_admin: méthode rattachée au journal MA.')


def uninstall_hook(env):
    """Supprime les méthodes de paiement via SQL pour permettre la réinstallation sans conflit."""
    cr = env.cr
    # 1. Supprimer les lignes de journal (account.payment.method.line)
    cr.execute("""
        DELETE FROM account_payment_method_line
        WHERE payment_method_id IN (
            SELECT id FROM account_payment_method WHERE code = 'mandat_administratif'
        )
    """)
    # 2. Supprimer account.payment.method
    cr.execute("DELETE FROM account_payment_method WHERE code = 'mandat_administratif'")
    # 3. Détacher payment.method des providers (many2many)
    cr.execute("""
        DELETE FROM payment_method_payment_provider_rel
        WHERE payment_method_id IN (
            SELECT id FROM payment_method WHERE code = 'mandat_administratif'
        )
    """)
    # 4. Supprimer payment.method
    cr.execute("DELETE FROM payment_method WHERE code = 'mandat_administratif'")
    _logger.info('mandat_admin: méthodes de paiement supprimées lors de la désinstallation.')
