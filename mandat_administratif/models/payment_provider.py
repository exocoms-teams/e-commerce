# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('mandat_administratif', "Mandat administratif")],
        ondelete={'mandat_administratif': 'set default'},
    )
    mandat_payment_delay = fields.Integer(
        string="Délai de paiement par défaut (jours)",
        default=30,
        help="Valeur informative utilisée uniquement quand le client n'a "
             "pas déclaré son type de structure. Le délai réel (30, 50 ou "
             "60 jours) est déterminé automatiquement par le « Type de "
             "structure publique » de la fiche client, déclarable par le "
             "client lui-même sur /my/mandat-administratif.",
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
        """N'afficher le mandat administratif qu'aux entités publiques et si publié/actif."""
        providers = super()._get_compatible_providers(
            company_id, partner_id, amount, **kwargs
        )
        # Filtrer d'abord pour ne garder que ce qui est publié/actif
        # Note: _get_compatible_providers de Odoo base gère déjà is_published/state.
        # Nous ajoutons notre contrainte métier spécifique.
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
