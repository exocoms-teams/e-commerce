# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

import pprint

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.payment.logging import get_payment_logger

_logger = get_payment_logger(__name__)


class RevolutController(http.Controller):
    _return_url = "/payment/revolut/return"
    _webhook_url = "/payment/revolut/webhook"

    @http.route(
        _return_url,
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
        save_session=False,
    )
    def revolut_return_from_checkout(self, **data):
        """Process the payment data after the customer returns from the Revolut checkout page.

        The route is flagged with `save_session=False` to prevent Odoo from assigning a new session
        to the user if they are redirected to this route with a POST request.

        :param dict data: The transaction reference (`ref`) embedded in the return URL.
        """
        _logger.info("Handling redirection from Revolut with data:\n%s", pprint.pformat(data))

        tx_sudo = request.env["payment.transaction"].sudo()._search_by_reference(
            "revolut", {"merchant_order_data": {"reference": data.get("ref")}}
        )
        if tx_sudo:
            self._fetch_and_record_order(tx_sudo, tx_sudo.provider_reference)
        return request.redirect("/payment/status")

    @http.route(_webhook_url, type="http", auth="public", methods=["POST"], csrf=False)
    def revolut_webhook(self):
        """Process the notification sent by Revolut to the webhook.

        :return: An empty string to acknowledge the notification.
        :rtype: str
        """
        raw_body = request.httprequest.get_data(as_text=True)
        headers = request.httprequest.headers
        _logger.info("Notification received from Revolut with data:\n%s", raw_body)

        try:
            notification_data = request.get_json_data()
        except ValueError:
            _logger.warning("Received a Revolut notification with an invalid JSON body.")
            return ""

        order_id = notification_data.get("order_id")
        if not order_id:
            _logger.warning("Received a Revolut notification without an order id.")
            return ""

        # The webhook is registered at the merchant account level: identify the provider that owns
        # the signing secret matching this notification.
        providers_sudo = request.env["payment.provider"].sudo().search([("code", "=", "revolut")])
        provider_sudo = next(
            (
                p for p in providers_sudo
                if p._revolut_verify_webhook_signature(
                    raw_body,
                    headers.get("Revolut-Request-Timestamp"),
                    headers.get("Revolut-Signature"),
                )
            ),
            None,
        )
        if not provider_sudo:
            _logger.warning("Received a Revolut notification with an invalid signature.")
            return ""

        self._fetch_and_record_order(provider_sudo, order_id)
        return ""  # Acknowledge the notification.

    @staticmethod
    def _fetch_and_record_order(record_sudo, order_id):
        """Fetch the order from Revolut and record it as the source of truth.

        :param record_sudo: A `payment.transaction` or `payment.provider` record able to reach the
                            Revolut API.
        :param str order_id: The id of the Revolut order to fetch.
        :return: None
        """
        if not order_id:
            return

        try:
            order_data = record_sudo._send_api_request("GET", f"orders/{order_id}")
        except ValidationError:
            _logger.exception("Unable to fetch the Revolut order %s.", order_id)
            return

        tx_sudo = request.env["payment.transaction"].sudo()._search_by_reference(
            "revolut", order_data
        )
        if tx_sudo:
            tx_sudo._record(order_data)
