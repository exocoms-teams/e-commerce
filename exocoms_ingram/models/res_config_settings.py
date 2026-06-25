from odoo import _, fields, models
from odoo.exceptions import UserError

from ..services.ingram_api import IngramApiClient


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    exocoms_ingram_client_id = fields.Char(
        string="Client ID",
        config_parameter="exocoms_ingram.client_id",
    )
    exocoms_ingram_client_secret = fields.Char(
        string="Client Secret",
        config_parameter="exocoms_ingram.client_secret",
    )
    exocoms_ingram_customer_number = fields.Char(
        string="Customer Number",
        config_parameter="exocoms_ingram.customer_number",
    )
    exocoms_ingram_country_code = fields.Char(
        string="Ingram Country Code",
        config_parameter="exocoms_ingram.country_code",
        default="US",
    )
    exocoms_ingram_sender_id = fields.Char(
        string="Sender ID",
        config_parameter="exocoms_ingram.sender_id",
        default="Exocoms",
    )

    def action_test_ingram_connection(self):
        self.ensure_one()
        if (
            not self.exocoms_ingram_client_id
            or not self.exocoms_ingram_client_secret
            or not self.exocoms_ingram_customer_number
        ):
            raise UserError(
                _("Renseigne au minimum Client ID, Client Secret et Customer Number.")
            )
        client = IngramApiClient(
            client_id=self.exocoms_ingram_client_id,
            client_secret=self.exocoms_ingram_client_secret,
            customer_number=self.exocoms_ingram_customer_number,
            country_code=self.exocoms_ingram_country_code or "US",
            sender_id=self.exocoms_ingram_sender_id or "Exocoms",
        )
        client.test_connection()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Ingram Micro"),
                "message": _("Connexion reussie."),
                "type": "success",
                "sticky": False,
            },
        }
