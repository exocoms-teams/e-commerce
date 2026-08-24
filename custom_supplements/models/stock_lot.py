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

        expiring_lots = lots.filtered(is_lot_expiring)
        _logger.warning('Lots : %s | Expired Lots : %s',lots,expiring_lots)
        if expiring_lots:
            for lot in expiring_lots:
                _logger.info(
                    'Produit : %s | Lot : %s | Expire le : %s',
                    lot.product_id.display_name,
                    lot.name,
                    lot.expiration_date,
                )

def is_lot_expiring(lot):
    alert_time = lot.product_id.product_tmpl_id.alert_time

    if not alert_time:
        return False

    alert_date = lot.expiration_date - timedelta(days=alert_time)

    _logger.info(
        "Lot %s | expiration=%s | délai=%s jours | "
        "date alerte=%s | maintenant=%s | expire bientôt=%s",
        lot.name,
        lot.expiration_date,
        alert_time,
        alert_date,
        now,
        alert_date <= now,
    )

    return alert_date <= now