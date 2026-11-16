
from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    x_exocoms_premium_theme = fields.Boolean(
        string="Activer le thème EXOCOMS Premium",
        default=False,
    )
