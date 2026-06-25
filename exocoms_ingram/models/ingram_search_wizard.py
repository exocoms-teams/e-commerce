import json

from odoo import _, fields, models
from odoo.exceptions import UserError


class IngramSearchWizard(models.TransientModel):
    _name = "exocoms.ingram.search.wizard"
    _description = "Recherche de produits Ingram"

    keyword = fields.Char(string="Mot-cle", required=True)
    page_size = fields.Integer(string="Taille de page", default=10)
    page_number = fields.Integer(string="Page", default=1)
    line_ids = fields.One2many(
        "exocoms.ingram.search.wizard.line",
        "wizard_id",
        string="Resultats",
    )

    def action_search(self):
        self.ensure_one()
        connector = self.env["exocoms.ingram.connector"]
        payload = connector.search_products(
            self.keyword,
            page_size=self.page_size,
            page_number=self.page_number,
        )
        products = connector._extract_product_results(payload)
        line_commands = [(5, 0, 0)]
        for product in products:
            line_commands.append(
                (0, 0, connector.format_search_payload(product))
            )
        self.write({"line_ids": line_commands})
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def action_import_selected(self):
        self.ensure_one()
        selected_lines = self.line_ids.filtered("selected")
        if not selected_lines:
            raise UserError(
                _("Selectionne au moins un produit a importer.")
            )
        connector = self.env["exocoms.ingram.connector"]
        payloads = [line.get_payload() for line in selected_lines]
        imported_products = connector.import_search_results(payloads)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Ingram Micro"),
                "message": _("%s produit(s) importe(s).")
                % len(imported_products),
                "type": "success",
                "sticky": False,
            },
        }


class IngramSearchWizardLine(models.TransientModel):
    _name = "exocoms.ingram.search.wizard.line"
    _description = "Ligne de resultat Ingram"

    wizard_id = fields.Many2one(
        "exocoms.ingram.search.wizard",
        required=True,
        ondelete="cascade",
    )
    selected = fields.Boolean(string="Importer", default=True)
    product_name = fields.Char(string="Nom")
    ingram_part_number = fields.Char(string="Ingram Part Number")
    vendor_part_number = fields.Char(string="Vendor Part Number")
    vendor_name = fields.Char(string="Vendor Name")
    description = fields.Text(string="Description")
    raw_payload = fields.Text(string="Payload brut")

    def get_payload(self):
        self.ensure_one()
        return json.loads(self.raw_payload or "{}")
