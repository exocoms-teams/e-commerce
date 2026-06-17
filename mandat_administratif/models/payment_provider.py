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

    def _get_default_payment_method_codes(self):
        if self.code == 'mandat_administratif':
            return ['mandat_administratif']
        return super()._get_default_payment_method_codes()
    
    def _should_build_inline_form(self, is_validation=False):
        if self.code == 'mandat_administratif':
            return True  # pas de redirection, formulaire inline
        return super()._should_build_inline_form(is_validation)
    
    def _get_redirect_form_view(self, is_validation=False):
        if self.code == 'mandat_administratif':
            return self.env.ref('mandat_administratif.mandat_inline_form')
        return super()._get_redirect_form_view(is_validation)


class PaymentTransactionMandat(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'mandat_administratif':
            return res
        return res

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'mandat_administratif':
            return
        self._set_pending()

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'mandat_administratif' or len(tx) == 1:
            return tx
        return tx
