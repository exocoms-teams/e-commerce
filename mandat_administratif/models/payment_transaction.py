# -*- coding: utf-8 -*-
from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_processing_values(self, processing_values):
        """ override de traitement """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'mandat_administratif':
            return res
        
        # On ne renvoie RIEN. C'est ce silence qui indique à Odoo 
        # qu'il n'y a pas de formulaire à soumettre ni de redirection externe !
        return {}

    def _process_notification_data(self, notification_data):
        """ override de validation """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'mandat_administratif':
            return

        # On simule le comportement du virement bancaire :
        # La commande passe en attente de validation administrative
        self._set_pending()
