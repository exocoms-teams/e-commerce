import json

from odoo import models, _
from odoo.exceptions import UserError

from ..services.ingram_api import IngramApiClient


class IngramConnector(models.AbstractModel):
    _name = "exocoms.ingram.connector"
    _description = "Connecteur Ingram Micro"

    def test_connection(self):
        client = self._get_client()
        return client.test_connection()

    def _get_client(self):
        params = self.env["ir.config_parameter"].sudo()

        client_id = params.get_param("exocoms_ingram.client_id")
        client_secret = params.get_param("exocoms_ingram.client_secret")
        customer_number = params.get_param("exocoms_ingram.customer_number")
        country_code = params.get_param("exocoms_ingram.country_code") or "US"
        sender_id = params.get_param("exocoms_ingram.sender_id") or "Exocoms"

        if not client_id or not client_secret or not customer_number:
            raise UserError(_("Les identifiants API Ingram ne sont pas configurés."))

        return IngramApiClient(
            client_id=client_id,
            client_secret=client_secret,
            customer_number=customer_number,
            country_code=country_code,
            sender_id=sender_id,
        )

    def _extract_product_results(self, payload):
        candidates = [
            payload.get("catalog"),
            payload.get("products"),
            payload.get("catalogResults"),
            payload.get("result"),
            payload.get("data"),
        ]
        for candidate in candidates:
            if isinstance(candidate, list):
                return candidate
            if isinstance(candidate, dict):
                nested = candidate.get("products") or candidate.get("items")
                if isinstance(nested, list):
                    return nested
        return []

    def _extract_order_number(self, payload):
        for key in ("orderNumber", "ingramOrderNumber", "order_id"):
            value = payload.get(key)
            if value:
                return value
        order = payload.get("order")
        if isinstance(order, dict):
            return order.get("orderNumber") or order.get("ingramOrderNumber")
        return False

    def _extract_confirmation_number(self, payload):
        for key in ("confirmationNumber", "confirmation_number"):
            value = payload.get(key)
            if value:
                return value
        order = payload.get("order")
        if isinstance(order, dict):
            return order.get("confirmationNumber")
        return False

    def _extract_order_status(self, payload):
        for key in ("orderStatus", "status", "state"):
            value = payload.get(key)
            if value:
                return value
        order = payload.get("order")
        if isinstance(order, dict):
            return order.get("orderStatus") or order.get("status")
        return False

    def search_products(self, keyword, page_size=10, page_number=1):
        client = self._get_client()
        return client.search_products(keyword, page_size, page_number)

    def get_product_details(self, ingram_part_number):
        client = self._get_client()
        return client.get_product_details(ingram_part_number)

    def get_price_and_availability(self, ingram_part_number):
        client = self._get_client()
        return client.get_price_and_availability([
            {"ingramPartNumber": ingram_part_number}
        ])

    def get_price_and_availability_for_products(self, products):
        client = self._get_client()
        return client.get_price_and_availability(products)

    def create_order_v7(self, payload):
        client = self._get_client()
        return client.create_order_v7(payload)

    def create_order_v6(self, payload):
        client = self._get_client()
        return client.create_order_v6(payload)

    def get_order(self, order_number):
        client = self._get_client()
        return client.get_order(order_number)

    def modify_order(self, order_number, payload, action_code=None):
        client = self._get_client()
        return client.modify_order(order_number, payload, action_code)

    def cancel_order(self, order_number):
        client = self._get_client()
        return client.cancel_order(order_number)

    def import_search_results(self, payloads):
        product_model = self.env["product.template"]
        imported = self.env["product.template"]
        for payload in payloads:
            imported |= product_model.create_or_update_from_ingram_data(payload)
        return imported

    def format_search_payload(self, payload):
        description = (
            payload.get("description")
            or payload.get("productDescription")
            or payload.get("name")
            or payload.get("productName")
            or payload.get("title")
            or payload.get("ingramPartNumber")
            or _("Produit Ingram")
        )
        return {
            "product_name": description,
            "ingram_part_number": payload.get("ingramPartNumber")
            or payload.get("partNumber")
            or payload.get("sku"),
            "vendor_part_number": payload.get("vendorPartNumber")
            or payload.get("manufacturerPartNumber"),
            "vendor_name": payload.get("vendorName")
            or payload.get("manufacturerName")
            or payload.get("brand"),
            "description": payload.get("description")
            or payload.get("productDescription")
            or "",
            "raw_payload": json.dumps(payload, ensure_ascii=False),
        }
