# -*- coding: utf-8 -*-
from odoo import fields, models

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

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'mandat_administratif':
            return
        self._set_pending()
