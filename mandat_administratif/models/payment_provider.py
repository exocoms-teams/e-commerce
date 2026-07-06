# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('mandat_administratif', "Mandat administratif")],
        ondelete={'mandat_administratif': 'set default'},
    )
    mandat_payment_delay = fields.Integer(
        string="Délai global de paiement (jours)",
        default=30,
    )
    mandat_require_engagement = fields.Boolean(
        string="Recommander le n° d'engagement juridique",
        default=True,
    )

    @api.model
    def _get_compatible_providers(self, company_id, partner_id, amount, **kwargs):
        providers = super()._get_compatible_providers(company_id, partner_id, amount, **kwargs)
        partner = self.env['res.partner'].browse(partner_id).exists()
        is_public = (
            partner
            and (partner.is_public_entity or partner.commercial_partner_id.is_public_entity)
        )
        if not is_public:
            providers = providers.filtered(lambda p: p.code != 'mandat_administratif')
        return providers

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != 'mandat_administratif':
            return super()._get_default_payment_method_codes()
        return ['mandat_administratif']
