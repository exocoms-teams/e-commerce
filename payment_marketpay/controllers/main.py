# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MarketpayController(http.Controller):

    @http.route('/payment/marketpay/return', type='http', auth='public', csrf=False, save_session=False)
    def marketpay_return(self, **data):
        """ Handle the return from Marketpay. """
        _logger.info("Marketpay: entering form_feedback with post data %s", pprint.pformat(data))
        if data:
            request.env['payment.transaction'].sudo()._handle_notification_data('marketpay', data)
        return request.redirect('/payment/status')

    @http.route('/payment/marketpay/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def marketpay_webhook(self, **data):
        """ Handle webhook notifications from Marketpay. """
        _logger.info("Marketpay: entering webhook with post data %s", pprint.pformat(data))
        if data:
            request.env['payment.transaction'].sudo()._handle_notification_data('marketpay', data)
        return ''
