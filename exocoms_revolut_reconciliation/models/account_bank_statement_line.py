# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    revolut_transaction_id = fields.Char(
        string="Identifiant Revolut",
        help="Identifiant du mouvement chez Revolut (leg id). Empêche la réimportation.",
        readonly=True,
        copy=False,
        index='btree_not_null',
    )
    revolut_order_id = fields.Char(
        string="Transaction Revolut",
        help="Identifiant de la transaction Revolut dont provient ce mouvement.",
        readonly=True,
        copy=False,
    )
    revolut_fee = fields.Monetary(
        string="Frais Revolut",
        help="Frais rapportés par Revolut sur ce mouvement. Donné à titre indicatif : "
             "aucune écriture n'est générée automatiquement.",
        readonly=True,
        copy=False,
    )

    _revolut_transaction_uniq = models.Constraint(
        'unique(journal_id, revolut_transaction_id)',
        "Ce mouvement Revolut est déjà importé dans ce journal.",
    )
