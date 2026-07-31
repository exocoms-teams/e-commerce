# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'mandat_administratif':
            return res
        return {
            'api_url': '/payment/mandat_administratif/process',
            'reference': self.reference,
        }

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        if provider_code != 'mandat_administratif':
            return super()._extract_reference(provider_code, payment_data)
        return payment_data.get('reference')

    def _process_notification_data(self, notification_data):
        """Mettre la transaction en attente."""
        # On laisse le super gérer les vérifications de base
        super()._process_notification_data(notification_data)

        if self.provider_code != 'mandat_administratif':
            return

        _logger.info(
            "Mandat administratif : transaction %s mise en attente (règlement via Chorus Pro).",
            self.reference,
        )

        # S'assurer que l'état passe à 'pending'
        if self.state != 'pending':
            self._set_pending()