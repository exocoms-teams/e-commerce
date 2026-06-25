from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ingram_part_number = fields.Char(string="Ingram Part Number", index=True)
    vendor_part_number = fields.Char(string="Vendor Part Number")
    vendor_name = fields.Char(string="Vendor Name")
    ingram_last_sync = fields.Datetime(string="Derniere synchronisation Ingram")
    ingram_available_qty = fields.Float(string="Stock Ingram disponible")
    ingram_last_price = fields.Float(string="Dernier prix Ingram")
    ingram_currency = fields.Char(string="Devise Ingram")

    def _extract_first_result(self, payload):
        if isinstance(payload, list) and payload:
            return payload[0]
        if isinstance(payload, dict):
            for key in (
                "products",
                "priceAndAvailability",
                "availability",
                "data",
                "result",
            ):
                value = payload.get(key)
                if isinstance(value, list) and value:
                    return value[0]
        return payload or {}

    def _extract_price_value(self, payload):
        candidates = [
            payload.get("customerPrice"),
            payload.get("netPrice"),
            payload.get("unitPrice"),
            payload.get("price"),
            payload.get("resellerPrice"),
        ]
        for candidate in candidates:
            if isinstance(candidate, (int, float)):
                return float(candidate)
            if isinstance(candidate, dict):
                value = candidate.get("value") or candidate.get("amount")
                if isinstance(value, (int, float)):
                    return float(value)
        return 0.0

    def _extract_currency_value(self, payload):
        for key in ("currencyCode", "currency", "currency_code"):
            value = payload.get(key)
            if value:
                return value
        price = payload.get("price")
        if isinstance(price, dict):
            return price.get("currencyCode") or price.get("currency")
        return False

    def _extract_qty_value(self, payload):
        candidates = [
            payload.get("availability"),
            payload.get("availabilityByWarehouse"),
            payload.get("availabilityInfo"),
            payload.get("quantityAvailable"),
            payload.get("availableQuantity"),
        ]
        for candidate in candidates:
            if isinstance(candidate, (int, float)):
                return float(candidate)
            if isinstance(candidate, dict):
                for key in ("availableQuantity", "quantityAvailable", "qty"):
                    value = candidate.get(key)
                    if isinstance(value, (int, float)):
                        return float(value)
            if isinstance(candidate, list):
                total = 0.0
                found = False
                for item in candidate:
                    if not isinstance(item, dict):
                        continue
                    for key in ("availableQuantity", "quantityAvailable", "qty"):
                        value = item.get(key)
                        if isinstance(value, (int, float)):
                            total += float(value)
                            found = True
                if found:
                    return total
        return 0.0

    @api.model
    def _prepare_vals_from_ingram_product(self, payload):
        name = (
            payload.get("description")
            or payload.get("productDescription")
            or payload.get("name")
            or payload.get("productName")
            or payload.get("title")
            or payload.get("ingramPartNumber")
            or _("Produit Ingram")
        )
        return {
            "name": name,
            "default_code": payload.get("vendorPartNumber")
            or payload.get("manufacturerPartNumber")
            or payload.get("ingramPartNumber"),
            "description_sale": payload.get("description")
            or payload.get("productDescription")
            or False,
            "sale_ok": True,
            "purchase_ok": True,
            "ingram_part_number": payload.get("ingramPartNumber")
            or payload.get("partNumber")
            or payload.get("sku"),
            "vendor_part_number": payload.get("vendorPartNumber")
            or payload.get("manufacturerPartNumber"),
            "vendor_name": payload.get("vendorName")
            or payload.get("manufacturerName")
            or payload.get("brand"),
            "ingram_last_sync": fields.Datetime.now(),
        }

    @api.model
    def create_or_update_from_ingram_data(self, payload):
        vals = self._prepare_vals_from_ingram_product(payload)
        ingram_part_number = vals.get("ingram_part_number")
        if not ingram_part_number:
            raise UserError(_("Le produit Ingram ne contient pas de part number."))

        product = self.search(
            [("ingram_part_number", "=", ingram_part_number)],
            limit=1,
        )
        if product:
            product.write(vals)
            return product
        return self.create(vals)

    def _apply_ingram_price_and_stock(self, payload):
        self.ensure_one()
        payload = self._extract_first_result(payload)
        vals = {
            "ingram_last_sync": fields.Datetime.now(),
            "ingram_last_price": self._extract_price_value(payload),
            "ingram_available_qty": self._extract_qty_value(payload),
            "ingram_currency": self._extract_currency_value(payload) or False,
        }
        if vals["ingram_last_price"]:
            vals["standard_price"] = vals["ingram_last_price"]
        self.write(vals)

    def action_sync_ingram_data(self):
        connector = self.env["exocoms.ingram.connector"]
        synced = 0
        for product in self:
            if not product.ingram_part_number:
                continue
            payload = connector.get_price_and_availability(product.ingram_part_number)
            product._apply_ingram_price_and_stock(payload)
            synced += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Ingram Micro"),
                "message": _("%s produit(s) synchronise(s).") % synced,
                "type": "success",
                "sticky": False,
            },
        }

    @api.model
    def cron_sync_ingram_products(self):
        products = self.search([("ingram_part_number", "!=", False)])
        if products:
            products.action_sync_ingram_data()
