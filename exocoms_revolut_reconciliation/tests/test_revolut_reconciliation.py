# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

import base64
import json
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

from odoo.addons.exocoms_revolut_reconciliation import const

# A throwaway RSA key, generated for the test suite only.
TEST_PRIVATE_KEY = None


def _generate_key():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


@tagged('post_install', '-at_install')
class TestRevolutReconciliation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        global TEST_PRIVATE_KEY
        if TEST_PRIVATE_KEY is None:
            TEST_PRIVATE_KEY = _generate_key()

        cls.account_id = 'b7ec67d3-5af1-42c8-bece-3d28nlmo894d'
        cls.connection = cls.env['revolut.business.connection'].create({
            'name': "Revolut Test",
            'client_id': 'client-id-123',
            'private_key': TEST_PRIVATE_KEY,
            'redirect_uri': 'https://exocoms.fr/revolut/business/callback',
        })
        cls.journal = cls.env['account.journal'].create({
            'name': "Revolut EUR",
            'type': 'bank',
            'code': 'RVLT',
            'revolut_connection_id': cls.connection.id,
            'revolut_account_id': cls.account_id,
            'revolut_sync_enabled': True,
        })

    def _transaction(self, tx_id='tx-1', leg_id='leg-1', amount=250.0, **kwargs):
        data = {
            'id': tx_id,
            'type': 'transfer',
            'state': 'completed',
            'created_at': '2026-03-02T09:15:00.000000Z',
            'completed_at': '2026-03-02T09:16:00.000000Z',
            'reference': 'Versement marchand',
            'legs': [{
                'leg_id': leg_id,
                'account_id': self.account_id,
                'amount': amount,
                'currency': 'EUR',
                'description': "Revolut Merchant settlement",
            }],
        }
        data.update(kwargs)
        return data

    # === JWT === #

    def test_client_assertion_has_the_claims_revolut_expects(self):
        assertion = self.connection._build_client_assertion()
        header_b64, payload_b64, signature_b64 = assertion.split('.')

        def decode(segment):
            return json.loads(base64.urlsafe_b64decode(segment + '=' * (-len(segment) % 4)))

        self.assertEqual(decode(header_b64)['alg'], 'RS256')
        payload = decode(payload_b64)
        self.assertEqual(payload['iss'], 'exocoms.fr')  # The redirect URI host, not the full URL.
        self.assertEqual(payload['sub'], 'client-id-123')
        self.assertEqual(payload['aud'], const.JWT_AUDIENCE)
        self.assertTrue(signature_b64)
        self.assertNotIn('=', assertion)  # Base64url padding must be stripped.

    def test_invalid_private_key_raises_a_readable_error(self):
        self.connection.private_key = "not a key"
        with self.assertRaises(UserError):
            self.connection._build_client_assertion()

    def test_redirect_uri_without_host_is_rejected(self):
        self.connection.redirect_uri = "callback"
        with self.assertRaises(UserError):
            self.connection._build_client_assertion()

    # === ENVIRONNEMENT === #

    def test_sandbox_is_the_default_host(self):
        self.assertEqual(self.connection._get_base_url(), const.API_BASE_URL_SANDBOX)
        self.connection.is_live = True
        self.assertEqual(self.connection._get_base_url(), const.API_BASE_URL_LIVE)

    def test_connection_state_reflects_the_refresh_token(self):
        self.assertEqual(self.connection.state, 'draft')
        self.connection.refresh_token = 'rt-123'
        self.assertEqual(self.connection.state, 'connected')

    # === IMPORT === #

    def test_transaction_becomes_a_statement_line(self):
        lines = self.journal._revolut_create_statement_lines([self._transaction()])

        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.amount, 250.0)
        self.assertEqual(lines.revolut_transaction_id, 'leg-1')
        self.assertEqual(lines.revolut_order_id, 'tx-1')
        self.assertEqual(str(lines.date), '2026-03-02')
        self.assertEqual(lines.payment_ref, "Revolut Merchant settlement")

    def test_importing_twice_creates_nothing_new(self):
        transaction = self._transaction()
        self.journal._revolut_create_statement_lines([transaction])
        again = self.journal._revolut_create_statement_lines([transaction])
        self.assertFalse(again)

    def test_pending_transactions_are_skipped(self):
        lines = self.journal._revolut_create_statement_lines([
            self._transaction(state='pending')
        ])
        self.assertFalse(lines)

    def test_legs_of_other_accounts_are_skipped(self):
        transaction = self._transaction()
        transaction['legs'][0]['account_id'] = 'another-account'
        self.assertFalse(self.journal._revolut_create_statement_lines([transaction]))

    def test_both_legs_of_an_internal_transfer_are_distinguished(self):
        """An internal transfer carries one leg per account; only ours must be imported."""
        transaction = self._transaction()
        transaction['legs'].append({
            'leg_id': 'leg-2',
            'account_id': 'another-account',
            'amount': -250.0,
            'currency': 'EUR',
        })
        lines = self.journal._revolut_create_statement_lines([transaction])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.revolut_transaction_id, 'leg-1')

    def test_fee_is_recorded_without_being_posted(self):
        transaction = self._transaction()
        transaction['legs'][0]['fee'] = 3.75
        lines = self.journal._revolut_create_statement_lines([transaction])
        self.assertEqual(lines.revolut_fee, 3.75)
        self.assertEqual(lines.amount, 250.0)  # The fee must not alter the imported amount.

    def test_merchant_name_becomes_the_partner_name(self):
        transaction = self._transaction(merchant={'name': "Acme Corp.", 'city': "Paris"})
        lines = self.journal._revolut_create_statement_lines([transaction])
        self.assertEqual(lines.partner_name, "Acme Corp.")

    def test_cross_currency_keeps_the_original_amount(self):
        transaction = self._transaction()
        transaction['legs'][0].update({'bill_amount': 212.5, 'bill_currency': 'GBP'})
        gbp = self.env.ref('base.GBP')
        gbp.active = True
        lines = self.journal._revolut_create_statement_lines([transaction])
        self.assertEqual(lines.foreign_currency_id, gbp)
        self.assertEqual(lines.amount_currency, 212.5)

    def test_raw_payload_is_kept_for_audit(self):
        lines = self.journal._revolut_create_statement_lines([self._transaction()])
        details = lines.transaction_details['revolut']
        self.assertEqual(details['transaction_id'], 'tx-1')
        self.assertEqual(details['type'], 'transfer')

    # === GARDE-FOUS === #

    def test_sync_without_account_id_is_refused(self):
        self.journal.revolut_account_id = False
        with self.assertRaises(UserError):
            self.journal.action_revolut_sync()

    def test_sync_on_a_non_bank_journal_is_refused(self):
        journal = self.env['account.journal'].create({
            'name': "Divers", 'type': 'general', 'code': 'RVMS',
            'revolut_connection_id': self.connection.id,
            'revolut_account_id': self.account_id,
        })
        with self.assertRaises(UserError):
            journal.action_revolut_sync()

    def test_cron_survives_a_failing_journal(self):
        """One broken journal must not stop the others from syncing."""
        with patch.object(
            type(self.journal), 'action_revolut_sync', side_effect=UserError("boom")
        ):
            self.connection.refresh_token = 'rt-123'
            self.env['revolut.business.connection']._cron_sync_revolut_transactions()
