import logging
from datetime import timedelta
from markupsafe import Markup, escape

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
                if not lot.expiration_notification_sent:
                    user = lot.product_id.responsible_id
                    lot.message_post(
                        body=Markup(
                            'Le lot <b>{}</b> du produit '
                            '<b>{}</b> expire le <b>{}</b>.'
                        ).format(
                            escape(lot.name),
                            escape(lot.product_id.display_name),
                            escape(lot.expiration_date),
                        ),
                        message_type='notification',
                        subtype_xmlid='mail.mt_comment',
                        partner_ids=[user.partner_id.id]
                    )
                    lot.expiration_notification_sent=True
                    

def is_lot_expiring_soon(lot):
    now = fields.Datetime.now()
    alert_time = lot.product_id.product_tmpl_id.alert_time

    if not alert_time:
        return False

    alert_date = lot.expiration_date - timedelta(days=alert_time)

    return alert_date <= now