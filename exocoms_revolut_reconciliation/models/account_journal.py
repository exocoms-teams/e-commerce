# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

import logging
from datetime import timedelta

from dateutil.parser import isoparse

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.exocoms_revolut_reconciliation import const

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    revolut_connection_id = fields.Many2one(
        'revolut.business.connection',
        string="Connexion Revolut",
        domain="[('company_id', '=', company_id)]",
        ondelete='set null',
    )
    revolut_sync_enabled = fields.Boolean(
        string="Synchroniser avec Revolut",
        help="Importe automatiquement les transactions du compte Revolut associé.",
    )
    revolut_account_id = fields.Char(
        string="Compte Revolut",
        help="Identifiant (UUID) du compte Revolut Business alimentant ce journal. "
             "Utilisez le bouton « Lister les comptes Revolut » pour le retrouver.",
    )
    revolut_sync_start_date = fields.Date(
        string="Importer à partir du",
        help="Aucune transaction antérieure à cette date ne sera importée.",
    )
    revolut_last_sync = fields.Datetime(string="Dernière synchronisation", readonly=True)

    # === ACTIONS === #

    def action_revolut_list_accounts(self):
        """Display the Revolut accounts reachable with the linked connection."""
        self.ensure_one()

        if not self.revolut_connection_id:
            raise UserError(_("Sélectionnez d'abord une connexion Revolut."))

        accounts = self.revolut_connection_id._api_get('accounts')
        lines = "\n".join(
            f"{a.get('currency')} — {a.get('name') or 'Sans nom'} : {a.get('id')}"
            for a in accounts
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'info',
                'sticky': True,
                'message': lines or _("Aucun compte Revolut n'est accessible."),
            },
        }

    def action_revolut_sync(self):
        """Import the Revolut transactions of this journal as bank statement lines."""
        for journal in self:
            journal._revolut_check_setup()
            transactions = journal._revolut_fetch_transactions()
            created = journal._revolut_create_statement_lines(transactions)
            journal.revolut_last_sync = fields.Datetime.now()
            _logger.info(
                "Revolut: %s new statement line(s) imported on journal %s.",
                len(created), journal.display_name,
            )
        return True

    def _revolut_check_setup(self):
        self.ensure_one()

        if not self.revolut_connection_id:
            raise UserError(_("Le journal %s n'est lié à aucune connexion Revolut.", self.name))
        if not self.revolut_account_id:
            raise UserError(_(
                "Renseignez l'identifiant du compte Revolut sur le journal %s.", self.name
            ))
        if self.type != 'bank':
            raise UserError(_("La synchronisation Revolut ne concerne que les journaux de banque."))

    # === RÉCUPÉRATION === #

    def _revolut_get_sync_from(self):
        """Return the datetime to fetch transactions from.

        A one-day overlap is kept on each run: Revolut can complete a transaction slightly after
        it was created, and duplicates are filtered out on the transaction id anyway.

        :return: The lower bound of the fetch window.
        :rtype: datetime
        """
        self.ensure_one()

        if self.revolut_last_sync:
            return self.revolut_last_sync - timedelta(days=1)
        if self.revolut_sync_start_date:
            return fields.Datetime.to_datetime(self.revolut_sync_start_date)
        return fields.Datetime.now() - timedelta(days=30)

    def _revolut_fetch_transactions(self):
        """Fetch the completed transactions of the Revolut account, paging backwards.

        :return: The transactions, oldest first.
        :rtype: list
        """
        self.ensure_one()

        sync_from = self._revolut_get_sync_from()
        transactions = []
        cursor = None
        while True:
            params = {
                'account': self.revolut_account_id,
                'from': sync_from.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'count': const.TRANSACTIONS_PAGE_SIZE,
            }
            if cursor:
                params['to'] = cursor
            page = self.revolut_connection_id._api_get('transactions', params=params)
            if not page:
                break
            transactions.extend(page)
            if len(page) < const.TRANSACTIONS_PAGE_SIZE:
                break
            # Revolut returns transactions newest first; page backwards on the oldest one.
            oldest = page[-1].get('created_at')
            if not oldest or oldest == cursor:
                break
            cursor = oldest

        return sorted(transactions, key=lambda t: t.get('created_at') or '')

    # === CRÉATION DES LIGNES === #

    def _revolut_create_statement_lines(self, transactions):
        """Turn Revolut transactions into bank statement lines, skipping known ones.

        :param list transactions: The transactions returned by the Business API.
        :return: The created statement lines.
        :rtype: recordset of `account.bank.statement.line`
        """
        self.ensure_one()

        candidates = {}
        for transaction in transactions:
            if transaction.get('state') not in const.IMPORTED_STATES:
                continue
            for leg in transaction.get('legs') or []:
                if leg.get('account_id') != self.revolut_account_id:
                    continue
                # A transaction between two own accounts has one leg per account: the leg id
                # identifies the movement on this journal's account.
                candidates[leg.get('leg_id') or transaction['id']] = (transaction, leg)

        if not candidates:
            return self.env['account.bank.statement.line']

        existing = set(self.env['account.bank.statement.line'].search([
            ('journal_id', '=', self.id),
            ('revolut_transaction_id', 'in', list(candidates)),
        ]).mapped('revolut_transaction_id'))

        values_list = [
            self._revolut_prepare_statement_line_values(transaction, leg, key)
            for key, (transaction, leg) in candidates.items()
            if key not in existing
        ]
        if not values_list:
            return self.env['account.bank.statement.line']
        return self.env['account.bank.statement.line'].create(values_list)

    def _revolut_prepare_statement_line_values(self, transaction, leg, unique_key):
        """Build the values of one bank statement line.

        :param dict transaction: The Revolut transaction.
        :param dict leg: The leg of that transaction affecting this journal's account.
        :param str unique_key: The identifier used to avoid re-importing the movement.
        :return: The creation values.
        :rtype: dict
        """
        self.ensure_one()

        date = transaction.get('completed_at') or transaction.get('created_at')
        amount = leg.get('amount') or 0.0
        values = {
            'journal_id': self.id,
            'date': isoparse(date).date() if date else fields.Date.context_today(self),
            'payment_ref': self._revolut_build_label(transaction, leg),
            'amount': amount,
            'ref': transaction.get('reference') or '',
            'transaction_type': transaction.get('type') or '',
            'revolut_transaction_id': unique_key,
            'revolut_order_id': transaction.get('id'),
            'revolut_fee': leg.get('fee') or 0.0,
            'transaction_details': {
                'revolut': {
                    'transaction_id': transaction.get('id'),
                    'leg_id': leg.get('leg_id'),
                    'type': transaction.get('type'),
                    'state': transaction.get('state'),
                    'request_id': transaction.get('request_id'),
                    'related_transaction_id': transaction.get('related_transaction_id'),
                    'reference': transaction.get('reference'),
                    'merchant': transaction.get('merchant'),
                    'card': transaction.get('card'),
                    'leg': leg,
                }
            },
        }

        merchant_name = (transaction.get('merchant') or {}).get('name')
        if merchant_name:
            values['partner_name'] = merchant_name

        # Cross-currency movements: keep the original amount alongside the account one.
        bill_currency = leg.get('bill_currency')
        leg_currency = leg.get('currency')
        if bill_currency and leg_currency and bill_currency != leg_currency:
            currency = self.env['res.currency'].search(
                [('name', '=', bill_currency)], limit=1
            )
            if currency:
                values['foreign_currency_id'] = currency.id
                values['amount_currency'] = leg.get('bill_amount') or 0.0

        partner = self._revolut_find_partner(transaction)
        if partner:
            values['partner_id'] = partner.id
        return values

    @staticmethod
    def _revolut_build_label(transaction, leg):
        """Return a readable label for the statement line."""
        parts = [
            leg.get('description'),
            (transaction.get('merchant') or {}).get('name'),
            transaction.get('reference'),
            transaction.get('type'),
        ]
        return next((part for part in parts if part), "Transaction Revolut")

    def _revolut_find_partner(self, transaction):
        """Try to guess the partner from a matching Odoo payment transaction.

        Only works when the Revolut reference carries an Odoo payment reference, which is the
        case for individual payouts, not for aggregated merchant settlements.

        :param dict transaction: The Revolut transaction.
        :return: The matching partner, if any.
        :rtype: recordset of `res.partner`
        """
        self.ensure_one()

        reference = transaction.get('reference')
        if not reference or 'payment.transaction' not in self.env.registry:
            return self.env['res.partner']
        payment_tx = self.env['payment.transaction'].sudo().search(
            [('reference', '=', reference)], limit=1
        )
        return payment_tx.partner_id
