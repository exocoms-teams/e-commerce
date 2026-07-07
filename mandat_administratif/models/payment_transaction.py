# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """Renvoyer les valeurs du formulaire de redirection.

        Comme pour le virement bancaire (payment_custom), le « paiement »
        consiste simplement à confirmer la commande : le formulaire poste la
        référence de transaction vers notre route de traitement qui met la
        transaction en attente. Le règlement réel interviendra hors ligne,
        par virement du comptable public après dépôt de la facture sur
        Chorus Pro.
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'mandat_administratif':
            return res
        return {
            'api_url': '/payment/mandat_administratif/process',
            'reference': self.reference,
        }

    # --- API de traitement des données de paiement (Odoo 19) --- #

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        """Extraire la référence de transaction des données reçues."""
        if provider_code != 'mandat_administratif':
            return super()._extract_reference(provider_code, payment_data)
        return payment_data.get('reference')

    @api.model
    def _extract_amount_data(self, provider_code, payment_data):
        """CORRECTIF : méthode manquante dans la version d'origine du
        module, provoquant un KeyError('amount') lors du paiement réel
        (confirmé en conditions réelles — Internal Server Error au
        clic sur « Payer maintenant »).

        Le formulaire de redirection de ce mode de paiement ne poste
        qu'une référence de transaction (pas de montant, cf.
        _get_specific_rendering_values ci-dessus) — exactement comme
        le virement bancaire natif (payment_custom). Il faut donc
        explicitement dire à Odoo de ne PAS valider de montant pour ce
        fournisseur, en renvoyant None ici (cf. commentaire natif dans
        payment_transaction.py : "Skip validation for transactions
        where the provider opts out of amount check").
        """
        if provider_code != 'mandat_administratif':
            return super()._extract_amount_data(provider_code, payment_data)
        return None

    def _apply_updates(self, payment_data):
        """Mettre la transaction en attente : le paiement se fera par
        virement administratif après dépôt de la facture sur Chorus Pro.
        """
        if self.provider_code != 'mandat_administratif':
            return super()._apply_updates(payment_data)
        _logger.info(
            "Mandat administratif : transaction %s mise en attente "
            "(règlement via Chorus Pro).", self.reference,
        )
        self._set_pending()