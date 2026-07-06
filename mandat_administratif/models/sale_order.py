# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_public_entity_partner = fields.Boolean(
        related='partner_id.commercial_partner_id.is_public_entity',
        string="Client entité publique",
    )
    engagement_juridique = fields.Char(
        string="N° d'engagement juridique",
        copy=False,
        help="Numéro d'engagement juridique (bon de commande) communiqué "
             "par l'entité publique. Reporté sur la facture et requis pour "
             "le dépôt sur Chorus Pro lorsque la structure l'exige.",
    )
    chorus_service_code = fields.Char(
        string="Code service (Chorus Pro)",
        compute='_compute_chorus_service_code',
        store=True,
        readonly=False,
        copy=False,
        help="Code service exécutant Chorus Pro. Pré-rempli depuis la "
             "fiche client.",
    )

    @api.depends('partner_id')
    def _compute_chorus_service_code(self):
        for order in self:
            if not order.chorus_service_code:
                order.chorus_service_code = (
                    order.partner_id.commercial_partner_id.chorus_service_code
                )

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals.update({
            'engagement_juridique': self.engagement_juridique,
            'chorus_service_code': self.chorus_service_code,
        })
        return vals
