import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockLot(models.Model):
    _inherit = 'stock.lot'

    @api.model
    def _cron_check_expiring_supplements(self):
        limit_date = fields.Datetime.now() + timedelta(days=30)
        expiring_lots = self.search([
            ('product_id.is_supplement', '=', True),
            ('expiration_date', '!=', False),
            ('expiration_date', '<=', limit_date),
        ])
        if expiring_lots:
            for lot in expiring_lots:
                _logger.info(
                    'Produit : %s | Lot : %s | Expire le : %s',
                    lot.product_id.display_name,
                    lot.name,
                    lot.expiration_date,
                )
