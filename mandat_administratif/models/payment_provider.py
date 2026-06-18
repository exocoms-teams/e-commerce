# -*- coding: utf-8 -*-
from odoo import fields, models

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('mandat_administratif', "Mandat Administratif")],
        ondelete={'mandat_administratif': 'set default'}
    )

    def _get_code_matching_providers(self, code):
        # On dit à Odoo d'associer notre code au comportement 'custom'
        if code == 'mandat_administratif':
            return self.filtered(lambda p: p.code == 'mandat_administratif')
        return super()._get_code_matching_providers(code)
