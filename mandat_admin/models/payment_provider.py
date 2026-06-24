# -*- coding: utf-8 -*-
from odoo import _, fields, models

try:
    from odoo.addons.payment import logging as payment_logging
    _logger = payment_logging.get_payment_logger(__name__)
except Exception:
    import logging
    _logger = logging.getLogger(__name__)


class PaymentProviderMandat(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('mandat_administratif', '🏛 Mandat Administratif')],
        ondelete={'mandat_administratif': 'set default'},
    )

    def _is_available_for_currency(self, currency):
        if self.code == 'mandat_administratif':
            return True
        return super()._is_available_for_currency(currency)


class PaymentTransactionMandat(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'mandat_administratif':
            return res
        return {
            'api_url': '/mandat/process',
            'reference': self.reference,
        }

    def _extract_amount_data(self, payment_data):
        if self.provider_code != 'mandat_administratif':
            return super()._extract_amount_data(payment_data)
        return None

    def _apply_updates(self, payment_data):
        if self.provider_code != 'mandat_administratif':
            return super()._apply_updates(payment_data)
        _logger.info("Mandat payment for transaction %s: set as pending.", self.reference)
        self._set_pending()

    def _log_received_message(self):
        other_txs = self.filtered(lambda t: t.provider_code != 'mandat_administratif')
        super(PaymentTransactionMandat, other_txs)._log_received_message()

    def _get_sent_message(self):
        message = super()._get_sent_message()
        if self.provider_code == 'mandat_administratif':
            message = _(
                "Le client a choisi %(provider_name)s pour effectuer le paiement.",
                provider_name=self.provider_id.name,
            )
        return message
