# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from werkzeug import urls

from odoo import _, models
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to return Marketpay-specific rendering values. """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'marketpay':
            return res

        base_url = self.provider_id.get_base_url()
        return_url = urls.url_join(base_url, '/payment/marketpay/return')
        webhook_url = urls.url_join(base_url, '/payment/marketpay/webhook')

        rendering_values = {
            'marketpay_merchant_id': self.provider_id.marketpay_merchant_id,
            'marketpay_amount': int(self.amount * 100), # typically minor units
            'marketpay_currency': self.currency_id.name,
            'marketpay_reference': self.reference,
            'marketpay_return_url': return_url,
            'marketpay_webhook_url': webhook_url,
        }

        # Normally you would compute a signature here based on the payload and the secret key
        rendering_values['marketpay_signature'] = "dummy_signature_for_now"
        return rendering_values

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on Marketpay data. """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'marketpay' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        if not reference:
            raise ValidationError("Marketpay: No reference found in the notification data.")

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'marketpay')])
        if not tx:
            raise ValidationError(
                "Marketpay: No transaction found matching reference %s." % reference
            )
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on Marketpay data. """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'marketpay':
            return

        # Update the provider reference
        self.provider_reference = notification_data.get('transaction_id')

        # Handle the payment state
        status = notification_data.get('status')
        if status == 'success':
            self._set_done()
        elif status == 'pending':
            self._set_pending()
        elif status == 'failed':
            self._set_error("Marketpay: Payment Failed.")
        elif status == 'canceled':
            self._set_canceled()
        else:
            _logger.warning("Marketpay: Received data with invalid payment status: %s", status)
            self._set_error("Marketpay: Invalid payment status.")
