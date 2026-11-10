from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    x_sneakers_theme = fields.Boolean("Activer le thème Sneakers")
