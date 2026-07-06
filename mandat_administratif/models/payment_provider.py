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
        help="Délai global de paiement applicable à l'acheteur public "
             "(30 jours pour l'État et les collectivités, 50 jours pour les "
             "établissements publics de santé).",
    )
    mandat_require_engagement = fields.Boolean(
        string="Recommander le n° d'engagement juridique",
        default=True,
        help="Affiche le n° d'engagement juridique comme information attendue "
             "sur les commandes des entités publiques (souvent exigé pour le "
             "dépôt sur Chorus Pro).",
    )

    # === MÉTHODES MÉTIER === #

    @api.model
    def _get_compatible_providers(self, company_id, partner_id, amount, **kwargs):
        """N'afficher le mandat administratif qu'aux entités publiques."""
        providers = super()._get_compatible_providers(
            company_id, partner_id, amount, **kwargs
        )
        partner = self.env['res.partner'].browse(partner_id).exists()
        if not partner or not partner.commercial_partner_id.is_public_entity:
            providers = providers.filtered(
                lambda p: p.code != 'mandat_administratif'
            )
        return providers

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != 'mandat_administratif':
            return super()._get_default_payment_method_codes()
        return ['mandat_administratif']
