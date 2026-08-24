import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockLot(models.Model):
    _inherit = 'stock.lot'
    expiration_notification_sent = fields.Boolean(default=False)
    @api.model
    def _cron_check_expiring_supplements(self):

        lots = self.search([
            ('product_id.is_supplement', '=', True),
            ('expiration_date', '!=', False),
        ])

        expiring_lots = lots.filtered(is_lot_expiring_soon)

        if expiring_lots:
            for lot in expiring_lots:
                if lot.expiration_notification_sent:
                    user = lot.product_id.responsible_id
                    _logger.warning('alert sent to user %s for lot %s.', user.name,lot.name)
                    lot.message_post(
                        body=(            
                            f'Le lot <b>{lot.name}</b> du produit '
                            f'<b>{lot.product_id.display_name}</b> '
                            f'expire le <b>{lot.expiration_date}</b>.'
                        ),
                        message_type='notification',
                        subtype_xmlid='mail.mt_comment',
                        partner_ids=[user.partner_id.id]
                    )

def is_lot_expiring_soon(lot):
    now = fields.Datetime.now()
    alert_time = lot.product_id.product_tmpl_id.alert_time

    if not alert_time:
        return False

    alert_date = lot.expiration_date - timedelta(days=alert_time)

    return alert_date <= now