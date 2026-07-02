from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('packlink', 'Packlink PRO')], ondelete={'packlink': 'set default'})
    oa_packlink_service_id = fields.Char(string='Packlink Service ID', help='The ID of the service in Packlink PRO (e.g. UPS Standard)')
    oa_packlink_default_dropoff = fields.Boolean(string='Is Dropoff Service', default=False)

    def packlink_rate_shipment(self, order):
        """
        Compute the shipping price for the given order using Packlink API.
        This is a stub ready to be connected to utils.packlink_api
        """
        api_key = self.env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.packlink_api_key')
        if not api_key:
            return {'success': False, 'price': 0.0, 'error_message': 'Packlink API Key is not configured.', 'warning_message': False}
            
        # In a real scenario, we would calculate the weight and dimensions
        # and query the Packlink API connector here.
        # For now, return a fixed placeholder rate if the key is present.
        return {'success': True, 'price': 15.0, 'error_message': False, 'warning_message': False}

    def packlink_send_shipping(self, pickings):
        """
        Send the shipment to Packlink PRO when the delivery is validated.
        """
        res = []
        for picking in pickings:
            # Here we would call the Packlink API to create the draft shipment
            # and potentially buy the label.
            # Then we store the tracking number:
            tracking_number = "PLK-MOCK-12345"
            
            res.append({
                'exact_price': 15.0,
                'tracking_number': tracking_number
            })
        return res

    def packlink_get_tracking_link(self, picking):
        """
        Return the custom tracking link on our frontend.
        """
        return f'/tracking/{picking.carrier_tracking_ref}'
