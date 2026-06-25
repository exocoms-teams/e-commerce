from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ingram_order_number = fields.Char(string="Numero de commande Ingram")
    ingram_confirmation_number = fields.Char(
        string="Numero de confirmation Ingram"
    )
    ingram_order_status = fields.Char(string="Statut Ingram")
    ingram_last_sync = fields.Datetime(
        string="Derniere synchronisation Ingram"
    )

    def _prepare_ingram_order_payload(self):
        self.ensure_one()
        shippable_lines = self.order_line.filtered(
            lambda line: not line.display_type and line.product_template_id
        )
        if not shippable_lines:
            raise UserError(_("La commande ne contient aucune ligne exploitable."))

        products_without_part = shippable_lines.filtered(
            lambda line: not line.product_template_id.ingram_part_number
        )
        if products_without_part:
            raise UserError(
                _(
                    "Certaines lignes n'ont pas de Ingram Part Number : %s"
                )
                % ", ".join(products_without_part.mapped("name"))
            )

        ship_partner = self.partner_shipping_id or self.partner_id
        return {
            "customerOrderNumber": self.name,
            "endCustomerOrderNumber": self.client_order_ref or self.name,
            "notes": self.note or "",
            "shipToInfo": {
                "companyName": ship_partner.name or "",
                "addressLine1": ship_partner.street or "",
                "addressLine2": ship_partner.street2 or "",
                "city": ship_partner.city or "",
                "postalCode": ship_partner.zip or "",
                "countryCode": ship_partner.country_id.code or "",
                "contact": {
                    "name": ship_partner.name or "",
                    "email": ship_partner.email or "",
                    "phone": ship_partner.phone or ship_partner.mobile or "",
                },
            },
            "lines": [
                {
                    "lineNumber": index,
                    "ingramPartNumber": line.product_template_id.ingram_part_number,
                    "quantity": line.product_uom_qty,
                    "customerPartNumber": (
                        line.product_id.default_code
                        or line.product_template_id.default_code
                        or ""
                    ),
                }
                for index, line in enumerate(shippable_lines, start=1)
            ],
        }

    def action_create_ingram_order(self):
        connector = self.env["exocoms.ingram.connector"]
        for order in self:
            payload = order._prepare_ingram_order_payload()
            response = connector.create_order_v7(payload)
            order.write(
                {
                    "ingram_order_number": (
                        connector._extract_order_number(response) or False
                    ),
                    "ingram_confirmation_number": (
                        connector._extract_confirmation_number(response) or False
                    ),
                    "ingram_order_status": (
                        connector._extract_order_status(response) or "submitted"
                    ),
                    "ingram_last_sync": fields.Datetime.now(),
                }
            )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Ingram Micro"),
                "message": _("Commande envoyee a Ingram."),
                "type": "success",
                "sticky": False,
            },
        }

    def action_sync_ingram_order_status(self):
        connector = self.env["exocoms.ingram.connector"]
        synced = 0
        for order in self.filtered("ingram_order_number"):
            response = connector.get_order(order.ingram_order_number)
            order.write(
                {
                    "ingram_order_status": (
                        connector._extract_order_status(response)
                        or order.ingram_order_status
                    ),
                    "ingram_confirmation_number": (
                        connector._extract_confirmation_number(response)
                        or order.ingram_confirmation_number
                    ),
                    "ingram_last_sync": fields.Datetime.now(),
                }
            )
            synced += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Ingram Micro"),
                "message": _("%s commande(s) synchronisee(s).") % synced,
                "type": "success",
                "sticky": False,
            },
        }
