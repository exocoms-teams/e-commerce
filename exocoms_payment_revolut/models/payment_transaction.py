# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import urls

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.const import CURRENCY_MINOR_UNITS
from odoo.addons.payment.logging import get_payment_logger
from odoo.addons.exocoms_payment_revolut import const
from odoo.addons.exocoms_payment_revolut.controllers.main import RevolutController

_logger = get_payment_logger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # === BUSINESS METHODS - PAYMENT FLOW === #

    def _get_specific_rendering_values(self, processing_values):
        """Override of `payment` to return Revolut-specific rendering values.

        Note: `self.ensure_one()` from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values.
        :return: The dict of provider-specific rendering values.
        :rtype: dict
        """
        if self.provider_code != 'revolut':
            return super()._get_specific_rendering_values(processing_values)

        payload = self._revolut_prepare_order_payload()
        try:
            order_data = self._send_api_request('POST', 'orders', json=payload)
        except ValidationError as error:
            self._set_error(str(error))
            return {}

        # Store the order id right away so the status can be fetched after redirection.
        self.provider_reference = order_data.get('id')

        checkout_url = order_data.get('checkout_url')
        if not checkout_url:
            self._set_error(_("Revolut n'a pas renvoyé d'URL de paiement pour cette commande."))
            return {}
        return {
            'api_url': checkout_url,
            'http_method': 'get',
            'url_params': payment_utils.extract_url_params(checkout_url),
        }

    def _revolut_prepare_order_payload(self):
        """Build the payload of the order creation request.

        Note: `self.ensure_one()`

        :return: The request payload.
        :rtype: dict
        """
        self.ensure_one()

        base_url = self.provider_id.get_base_url()
        return_url = urls.urljoin(base_url, RevolutController._return_url)
        payload = {
            'amount': payment_utils.to_minor_currency_units(self.amount, self.currency_id),
            'currency': self.currency_id.name,
            'description': self.reference,
            'capture_mode': 'manual' if self.provider_id.capture_manually else 'automatic',
            'merchant_order_data': {'reference': self.reference},
            'metadata': {'odoo_reference': self.reference},
            # Revolut does not echo the reference on redirection: carry it in the return URL.
            'redirect_url': f'{return_url}?ref={self.reference}',
        }
        if self.partner_email:
            payload['customer'] = {
                'email': self.partner_email,
                'full_name': self.partner_name or '',
                'phone': self.partner_phone or '',
            }
            payload['customer'] = {k: v for k, v in payload['customer'].items() if v}
        return payload

    def _send_capture_request(self):
        """Override of `payment` to send a capture request to Revolut.

        Note: `self.ensure_one()` from `_capture`

        :return: None
        """
        if self.provider_code != 'revolut':
            return super()._send_capture_request()

        source_tx = self.source_transaction_id
        payload = {
            'amount': payment_utils.to_minor_currency_units(self.amount, self.currency_id),
        }
        order_data = self._send_api_request(
            'POST',
            f'orders/{source_tx.provider_reference}/capture',
            json=payload,
            idempotency_key=payment_utils.generate_idempotency_key(self, scope='capture'),
        )
        self.provider_reference = source_tx.provider_reference
        self._record(order_data)

    def _send_void_request(self):
        """Override of `payment` to send a void request to Revolut.

        Revolut cancels the whole outstanding authorization; partial voids are performed implicitly
        by capturing a smaller amount.

        Note: `self.ensure_one()` from `_void`

        :return: None
        """
        if self.provider_code != 'revolut':
            return super()._send_void_request()

        source_tx = self.source_transaction_id
        order_data = self._send_api_request(
            'POST', f'orders/{source_tx.provider_reference}/cancel'
        )
        self.provider_reference = source_tx.provider_reference
        self._record(order_data)

    def _send_refund_request(self):
        """Override of `payment` to send a refund request to Revolut.

        Note: `self.ensure_one()` from `_refund`

        :return: None
        """
        if self.provider_code != 'revolut':
            return super()._send_refund_request()

        source_tx = self.source_transaction_id
        payload = {
            # Odoo stores refund amounts as negatives; Revolut expects a positive amount.
            'amount': payment_utils.to_minor_currency_units(-self.amount, self.currency_id),
            'currency': self.currency_id.name,
            'description': self.reference,
            'merchant_order_data': {'reference': self.reference},
            'metadata': {'odoo_reference': self.reference},
        }
        refund_data = self._send_api_request(
            'POST',
            f'orders/{source_tx.provider_reference}/refund',
            json=payload,
            idempotency_key=payment_utils.generate_idempotency_key(self, scope='refund'),
        )
        self.provider_reference = refund_data.get('id')
        self._record(refund_data)

    # === BUSINESS METHODS - PROCESSING === #

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        """Override of `payment` to extract the reference from the payment data."""
        if provider_code != 'revolut':
            return super()._extract_reference(provider_code, payment_data)

        return (
            (payment_data.get('merchant_order_data') or {}).get('reference')
            or (payment_data.get('metadata') or {}).get('odoo_reference')
            or payment_data.get('merchant_order_ext_ref')
        )

    def _extract_amount_data(self, payment_data):
        """Override of `payment` to extract the amount and currency from the payment data."""
        if self.provider_code != 'revolut':
            return super()._extract_amount_data(payment_data)

        currency_code = payment_data.get('currency')
        if not currency_code:
            return None  # Opt out of the amount check when the data is incomplete.
        if self.source_transaction_id and self.operation != 'refund':
            # Capture and void orders keep reporting the amount of the source order, which differs
            # from the child transaction's amount on partial operations.
            return None

        precision_digits = CURRENCY_MINOR_UNITS.get(
            currency_code, self.currency_id.decimal_places
        )
        return {
            'amount': payment_utils.to_major_currency_units(
                payment_data.get('amount') or 0, self.currency_id, precision_digits
            ),
            'currency_code': currency_code,
            'precision_digits': precision_digits,
        }

    def _apply_updates(self, payment_data):
        """Override of `payment` to update the transaction based on the payment data."""
        if self.provider_code != 'revolut':
            return super()._apply_updates(payment_data)

        if payment_data.get('id'):
            self.provider_reference = payment_data['id']

        # Update the payment method based on the last payment attempt of the order.
        payments = payment_data.get('payments') or []
        if payments:
            method_type = (payments[-1].get('payment_method') or {}).get('type', '')
            method_type = const.PAYMENT_METHOD_TYPE_NORMALIZATION.get(method_type, method_type)
            payment_method = self.provider_id._get_pm_from_code(
                method_type, mapping=const.PAYMENT_METHODS_MAPPING
            )
            self.payment_method_id = payment_method or self.payment_method_id

        # Update the payment state.
        order_state = payment_data.get('state')
        if order_state in const.PAYMENT_STATUS_MAPPING['pending']:
            # A captured or refunded order transits through `processing` before settlement. For the
            # child transactions that carry the capture or the refund, the operation is already
            # irreversible, so they are marked as done immediately.
            if order_state == 'processing' and self.source_transaction_id:
                self._set_done()
            else:
                self._set_pending()
        elif order_state in const.PAYMENT_STATUS_MAPPING['authorized']:
            self._set_authorized()
        elif order_state in const.PAYMENT_STATUS_MAPPING['done']:
            self._set_done()
        elif order_state in const.PAYMENT_STATUS_MAPPING['cancel']:
            self._set_canceled(_("Commande Revolut annulée."))
        elif order_state in const.PAYMENT_STATUS_MAPPING['error']:
            self._set_error(_(
                "Le paiement a été refusé par Revolut : %s",
                self._revolut_get_decline_reason(payment_data),
            ))
        else:
            _logger.warning(
                "Received data with invalid order state (%s) for transaction %s.",
                order_state, self.reference,
            )
            self._set_error(_("Statut de commande Revolut inconnu : %s.", order_state))

    @staticmethod
    def _revolut_get_decline_reason(payment_data):
        """Return the decline reason of the last payment of an order, if any.

        :param dict payment_data: The order data sent by Revolut.
        :return: The decline reason.
        :rtype: str
        """
        payments = payment_data.get('payments') or []
        if not payments:
            return _("raison inconnue")
        last_payment = payments[-1]
        return (
            last_payment.get('decline_reason')
            or last_payment.get('bank_message')
            or _("raison inconnue")
        )
