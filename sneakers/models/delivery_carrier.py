from odoo import models, fields, _
from odoo.exceptions import UserError
import requests
import json
import base64
import logging

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[
            ("sendcloud", "SendCloud"),
        ],
        ondelete={
            "sendcloud": "set default",
        },
    )

    sendcloud_public_key = fields.Char(
        string="SendCloud Public Key",
        copy=False,
    )

    sendcloud_secret_key = fields.Char(
        string="SendCloud Secret Key",
        copy=False,
    )

    sendcloud_shipping_method_id = fields.Many2one(
        "sendcloud.shipping.method",
        string="SendCloud Shipping Method",
    )

    sendcloud_test_result = fields.Text(
        string="SendCloud Test Result",
        readonly=True,
    )

    def _sendcloud_auth(self):
        self.ensure_one()

        if not self.sendcloud_public_key or not self.sendcloud_secret_key:
            raise UserError(
                _("Please configure SendCloud Public Key and Secret Key.")
            )

        credentials = (
            f"{self.sendcloud_public_key}:{self.sendcloud_secret_key}"
        )

        token = base64.b64encode(
            credentials.encode()
        ).decode()

        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }

    def action_test_sendcloud_connection(self):
        self.ensure_one()

        url = "https://panel.sendcloud.sc/api/v2/user"

        try:
            response = requests.get(
                url,
                headers=self._sendcloud_auth(),
                timeout=15,
            )

            if response.status_code == 200:
                self.sendcloud_test_result = (
                    "SUCCESS: SendCloud connection successful."
                )
                return True

            self.sendcloud_test_result = (
                f"FAILED HTTP {response.status_code}: {response.text}"
            )

        except Exception as error:
            _logger.exception(
                "SendCloud connection error"
            )

            self.sendcloud_test_result = str(error)

        return False


    def sendcloud_rate_shipment(self, order):

        self.ensure_one()

        method = self.sendcloud_shipping_method_id

        if not method:
            return {
                "success": False,
                "price": 0,
                "error_message": "No SendCloud method selected",
            }


        # Calcul du poids total
        total_weight = sum(
            line.product_id.weight * line.product_uom_qty
            for line in order.order_line
            if line.product_id
        )


        # Vérification poids
        if not (
            method.min_weight <= total_weight <= method.max_weight
        ):
            return {
                "success": False,
                "price": 0,
                "error_message": (
                    "SendCloud method unavailable "
                    "for this package weight."
                ),
            }


        country_code = (
            order.partner_shipping_id
            .country_id
            .code
        )


        countries = json.loads(
            method.country_prices or "[]"
        )


        price = None


        for country in countries:

            if country.get("iso_2") == country_code:

                price = country.get(
                    "price"
                )

                break


        # Pays non supporté
        if price is None:

            return {
                "success": False,
                "price": 0,
                "error_message": (
                    "SendCloud does not support "
                    "this destination country."
                ),
            }


        return {
            "success": True,
            "price": price,
            "error_message": False,
            "warning_message": False,
        }


    def sendcloud_send_shipping(self, pickings):
        self.ensure_one()

        result = []

        for picking in pickings:
            result.append({
                "exact_price": 0.0,
                "tracking_number": False,
            })

        return result


    def sendcloud_get_tracking_link(self, picking):
        self.ensure_one()

        if not picking.carrier_tracking_ref:
            return False

        return (
            "https://tracking.sendcloud.sc/"
            + picking.carrier_tracking_ref
        )


    def sendcloud_cancel_shipment(self, picking):
        self.ensure_one()

        return True

    def action_import_sendcloud_shipping_methods(self):
        self.ensure_one()

        url = "https://panel.sendcloud.sc/api/v2/shipping_methods"

        try:
            response = requests.get(
                url,
                headers=self._sendcloud_auth(),
                timeout=30,
            )

            if response.status_code != 200:
                raise UserError(
                    _(
                        "SendCloud API Error:\n%s"
                        % response.text
                    )
                )

            data = response.json()

            shipping_methods = data.get(
                "shipping_methods",
                []
            )

            if not shipping_methods:
                raise UserError(
                    _("No shipping methods returned by SendCloud.")
                )


            ShippingMethod = self.env[
                "sendcloud.shipping.method"
            ]

            created = 0
            updated = 0


            for method in shipping_methods:

                countries = method.get("countries", [])

                values = {
                    "name": method.get("name"),
                    "sendcloud_id": method.get("id"),
                    "carrier": method.get("carrier"),
                    "min_weight": float(method.get("min_weight") or 0),
                    "max_weight": float(method.get("max_weight") or 0),
                    "price": float(method.get("price") or 0),

                    "country_prices": json.dumps(
                        countries
                    ),
                }
                existing = ShippingMethod.search(
                    [
                        (
                            "sendcloud_id",
                            "=",
                            method.get("id")
                        )
                    ],
                    limit=1
                )


                if existing:
                    existing.write(values)
                    updated += 1

                else:
                    ShippingMethod.create(values)
                    created += 1


            self.sendcloud_test_result = (
                "SUCCESS: Imported %s methods, updated %s methods."
                % (
                    created,
                    updated,
                )
            )

            return True


        except Exception as error:

            _logger.exception(
                "SendCloud import shipping methods error"
            )

            raise UserError(
                str(error)
            )
