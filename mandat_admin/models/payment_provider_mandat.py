# -*- coding: utf-8 -*-
from odoo import models, fields, _


class PaymentProviderMandat(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('mandat_administratif', 'Mandat Administratif')],
        ondelete={'mandat_administratif': 'set default'},
    )

    def _get_supported_currencies(self):
        supported = super()._get_supported_currencies()
        if self.code == 'mandat_administratif':
            supported = supported.filtered(lambda c: c.name == 'EUR')
        return supported
