from odoo import models, api
import requests
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.amount_total > 150:
                self._send_n8n_vip_alert(order)
        return res

    def _send_n8n_vip_alert(self, order):
        url = "http://82.165.251.136:5678/webhook-test/85317b44-5cc8-4dcc-a2b0-14d6930912ed"
        payload = {
            "order_id": order.id,
            "order_name": order.name,
            "customer_name": order.partner_id.name,
            "amount_total": order.amount_total,
            "state": order.state
        }
        try:
            # Run the post request silently, with a 3-second timeout to avoid locking the UI
            requests.post(url, json=payload, timeout=3)
            _logger.info("Webhook sent successfully to n8n for VIP order %s", order.name)
        except Exception as e:
            _logger.warning("Failed to send webhook to n8n for VIP order %s: %s", order.name, str(e))
