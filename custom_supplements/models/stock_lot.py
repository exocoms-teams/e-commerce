import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockLot(models.Model):
    _inherit = 'stock.lot'

    @api.model
    def _cron_check_expiring_supplements(self):

        now = fields.Datetime.now()
        lots = self.search([
            ('product_id.is_supplement', '=', True),
            ('expiration_date', '!=', False),
        ])

        expiring_lots = lots.filtered(
            lambda lot: lot.expiration_date - timedelta(
                days=lot.product_id.product_tmpl_id.alert_time
            ) >= now
        )
        _logger.info(expiring_lots)
        if expiring_lots:
            for lot in expiring_lots:
                _logger.info(
                    'Produit : %s | Lot : %s | Expire le : %s',
                    lot.product_id.display_name,
                    lot.name,
                    lot.expiration_date,
                )
