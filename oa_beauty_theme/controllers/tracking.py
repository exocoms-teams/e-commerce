from odoo import http
from odoo.http import request
from ..utils.packlink_api import PacklinkAPIConnector
import logging

_logger = logging.getLogger(__name__)

class TrackingController(http.Controller):

    @http.route(['/tracking', '/tracking/<string:tracking_number>'], type='http', auth='public', website=True)
    def render_tracking_page(self, tracking_number=None, **kw):
        """
        Renders the luxury tracking page for customers.
        If a tracking number is provided, fetches the status from Packlink PRO.
        """
        tracking_data = None
        error_message = None

        if tracking_number:
            api_key = request.env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.packlink_api_key')
            sandbox = request.env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.packlink_sandbox')
            
            # Use the modular connector
            connector = PacklinkAPIConnector(api_key, sandbox=sandbox)
            tracking_data = connector.get_tracking(tracking_number)

            if not tracking_data:
                error_message = "Nous n'avons pas pu trouver de colis avec ce numéro de suivi."

        values = {
            'tracking_number': tracking_number,
            'tracking_data': tracking_data,
            'error_message': error_message,
        }

        # Render the QWeb template (to be added in website_core_pages.xml)
        return request.render('oa_beauty_theme.page_order_tracking', values)
