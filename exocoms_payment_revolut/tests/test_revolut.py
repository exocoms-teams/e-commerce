# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

import hashlib
import hmac
import time
from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.exocoms_payment_revolut import const
from odoo.addons.exocoms_payment_revolut.tests.common import RevolutCommon


@tagged('post_install', '-at_install')
class TestRevolutProvider(RevolutCommon):

    # === REQUEST HELPERS === #

    def test_api_url_follows_is_live(self):
        """The sandbox host is used until the provider goes live."""
        self.provider.is_live = False
        self.assertEqual(
            self.provider._build_request_url('orders'),
            'https://sandbox-merchant.revolut.com/api/orders',
        )
        self.provider.is_live = True
        self.assertEqual(
            self.provider._build_request_url('orders'),
            'https://merchant.revolut.com/api/orders',
        )

    def test_headers_carry_api_version_and_key(self):
        headers = self.provider._build_request_headers('POST', 'orders', None)
        self.assertEqual(headers['Revolut-Api-Version'], const.API_VERSION)
        self.assertEqual(headers['Authorization'], 'Bearer sk_dummy_secret_key')
        self.assertNotIn('Idempotency-Key', headers)

    def test_headers_carry_idempotency_key_when_given(self):
        headers = self.provider._build_request_headers(
            'POST', 'orders', None, idempotency_key='abc123'
        )
        self.assertEqual(headers['Idempotency-Key'], 'abc123')

    # === WEBHOOK SIGNATURE === #

    def _sign(self, body, timestamp, secret='wsk_dummy_signing_secret'):
        return 'v1=' + hmac.new(
            secret.encode(), f'v1.{timestamp}.{body}'.encode(), hashlib.sha256
        ).hexdigest()

    def test_valid_signature_is_accepted(self):
        body, ts = '{"event":"ORDER_COMPLETED"}', str(int(time.time() * 1000))
        self.assertTrue(
            self.provider._revolut_verify_webhook_signature(body, ts, self._sign(body, ts))
        )

    def test_tampered_body_is_rejected(self):
        body, ts = '{"event":"ORDER_COMPLETED"}', str(int(time.time() * 1000))
        signature = self._sign(body, ts)
        self.assertFalse(
            self.provider._revolut_verify_webhook_signature(
                '{"event":"ORDER_CANCELLED"}', ts, signature
            )
        )

    def test_replayed_notification_is_rejected(self):
        """A notification older than the tolerance must not be replayable."""
        body = '{"event":"ORDER_COMPLETED"}'
        stale = str(int(time.time() * 1000) - const.WEBHOOK_TIMESTAMP_TOLERANCE_MS - 1000)
        self.assertFalse(
            self.provider._revolut_verify_webhook_signature(body, stale, self._sign(body, stale))
        )

    def test_signature_of_another_secret_is_rejected(self):
        body, ts = '{"event":"ORDER_COMPLETED"}', str(int(time.time() * 1000))
        self.assertFalse(
            self.provider._revolut_verify_webhook_signature(
                body, ts, self._sign(body, ts, secret='wsk_someone_else')
            )
        )

    def test_rotated_secret_accepts_any_matching_signature(self):
        """Revolut sends several signatures while a secret is being rotated."""
        body, ts = '{"event":"ORDER_COMPLETED"}', str(int(time.time() * 1000))
        header = f"{self._sign(body, ts, secret='wsk_old')},{self._sign(body, ts)}"
        self.assertTrue(self.provider._revolut_verify_webhook_signature(body, ts, header))

    def test_missing_secret_rejects_everything(self):
        self.provider.revolut_webhook_secret = False
        body, ts = '{}', str(int(time.time() * 1000))
        self.assertFalse(self.provider._revolut_verify_webhook_signature(body, ts, 'v1=whatever'))

    def test_malformed_headers_are_rejected(self):
        body = '{}'
        self.assertFalse(self.provider._revolut_verify_webhook_signature(body, None, 'v1=x'))
        self.assertFalse(self.provider._revolut_verify_webhook_signature(body, 'not-a-ts', 'v1=x'))
        self.assertFalse(self.provider._revolut_verify_webhook_signature(body, '123', None))


@tagged('post_install', '-at_install')
class TestRevolutTransaction(RevolutCommon):

    # === ORDER CREATION === #

    def test_order_payload_uses_minor_units_and_reference(self):
        tx = self._create_transaction(flow='redirect')
        payload = tx._revolut_prepare_order_payload()

        self.assertEqual(payload['amount'], 111111)
        self.assertEqual(payload['currency'], 'EUR')
        self.assertEqual(payload['merchant_order_data']['reference'], self.reference)
        self.assertEqual(payload['capture_mode'], 'automatic')
        self.assertIn(f'ref={self.reference}', payload['redirect_url'])

    def test_manual_capture_switches_the_capture_mode(self):
        self.provider.capture_manually = True
        tx = self._create_transaction(flow='redirect')
        self.assertEqual(tx._revolut_prepare_order_payload()['capture_mode'], 'manual')

    def test_rendering_values_redirect_to_the_checkout_url(self):
        tx = self._create_transaction(flow='redirect')
        with patch.object(
            type(tx), '_send_api_request', return_value=self._build_order_data(state='pending')
        ):
            values = tx._get_specific_rendering_values(None)

        self.assertEqual(values['api_url'], self.checkout_url)
        self.assertEqual(values['http_method'], 'get')
        self.assertEqual(tx.provider_reference, self.order_id)

    def test_missing_checkout_url_sets_the_transaction_in_error(self):
        tx = self._create_transaction(flow='redirect')
        order = self._build_order_data(state='pending')
        del order['checkout_url']
        with patch.object(type(tx), '_send_api_request', return_value=order):
            tx._get_specific_rendering_values(None)

        self.assertEqual(tx.state, 'error')

    # === DATA EXTRACTION === #

    def test_reference_is_read_from_the_merchant_order_data(self):
        tx = self._create_transaction(flow='redirect')
        found = self.env['payment.transaction']._search_by_reference(
            'revolut', self._build_order_data()
        )
        self.assertEqual(found, tx)

    def test_reference_falls_back_to_the_metadata(self):
        order = self._build_order_data()
        del order['merchant_order_data']
        self.assertEqual(
            self.env['payment.transaction']._extract_reference('revolut', order), self.reference
        )

    def test_amount_is_converted_back_to_major_units(self):
        tx = self._create_transaction(flow='redirect')
        amount_data = tx._extract_amount_data(self._build_order_data())
        self.assertEqual(amount_data['amount'], 1111.11)
        self.assertEqual(amount_data['currency_code'], 'EUR')

    def test_amount_check_is_skipped_for_capture_children(self):
        """Revolut reports the source order amount on partial captures."""
        source_tx = self._create_transaction(flow='redirect', state='authorized')
        child_tx = source_tx._create_child_transaction(500.0)
        self.assertIsNone(child_tx._extract_amount_data(self._build_order_data()))

    def test_amount_check_still_applies_to_refunds(self):
        source_tx = self._create_transaction(flow='redirect', state='done')
        refund_tx = source_tx._create_child_transaction(500.0, is_refund=True)
        amount_data = refund_tx._extract_amount_data(
            self._build_order_data(amount=50000)
        )
        self.assertEqual(amount_data['amount'], 500.0)

    # === STATE MAPPING === #

    def test_order_states_map_to_transaction_states(self):
        for order_state, expected in [
            ('pending', 'pending'),
            ('processing', 'pending'),
            ('authorised', 'authorized'),
            ('completed', 'done'),
            ('cancelled', 'cancel'),
            ('failed', 'error'),
        ]:
            with self.subTest(order_state=order_state):
                tx = self._create_transaction(
                    flow='redirect', reference=f'ref-{order_state}'
                )
                tx._apply_updates(self._build_order_data(state=order_state))
                self.assertEqual(tx.state, expected)

    def test_unknown_order_state_sets_an_error(self):
        tx = self._create_transaction(flow='redirect')
        tx._apply_updates(self._build_order_data(state='teleported'))
        self.assertEqual(tx.state, 'error')

    def test_processing_marks_capture_children_as_done(self):
        """A capture is irreversible on Revolut's side even before settlement."""
        source_tx = self._create_transaction(flow='redirect', state='authorized')
        child_tx = source_tx._create_child_transaction(1111.11)
        child_tx._apply_updates(self._build_order_data(state='processing'))
        self.assertEqual(child_tx.state, 'done')

    def test_provider_reference_is_stored(self):
        tx = self._create_transaction(flow='redirect')
        tx._apply_updates(self._build_order_data())
        self.assertEqual(tx.provider_reference, self.order_id)

    def test_revolut_pay_variants_map_to_the_same_method(self):
        for revolut_type in ('revolut_pay_card', 'revolut_pay_account'):
            with self.subTest(revolut_type=revolut_type):
                normalized = const.PAYMENT_METHOD_TYPE_NORMALIZATION.get(revolut_type)
                self.assertEqual(normalized, 'revolut_pay')

    def test_decline_reason_is_surfaced_in_the_error(self):
        tx = self._create_transaction(flow='redirect')
        tx._apply_updates(self._build_order_data(
            state='failed',
            payments=[{
                'payment_method': {'type': 'card'},
                'decline_reason': 'insufficient_funds',
            }],
        ))
        self.assertEqual(tx.state, 'error')
        self.assertIn('insufficient_funds', tx.state_message)
