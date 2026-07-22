from odoo import models, fields, api
import logging
from datetime import timedelta

# Initialisation du logger pour remonter l'information dans le terminal
_logger = logging.getLogger(__name__)

class StockLot(models.Model):
    _inherit = 'stock.lot'

    @api.model
    def _cron_check_expiring_supplements(self):
        """ Vérifie chaque nuit les compléments expirant dans moins de 30 jours """
        
        # Calcul de la date limite (Aujourd'hui + 30 jours)
        limit_date = fields.Datetime.now() + timedelta(days=30)
        
        # Requête ORM de recherche
        expiring_lots = self.search([
            ('product_id.is_supplement', '=', True),
            ('expiration_date', '<=', limit_date),
            ('expiration_date', '!=', False) # Exclure les lots sans date
        ])
        
        # Traitement des résultats
        if expiring_lots:
            _logger.warning(f"ALERTE INVENTAIRE : {len(expiring_lots)} lot(s) de compléments arrivent à péremption !")
            for lot in expiring_lots:
                _logger.info(f" - Produit : {lot.product_id.name} | Lot : {lot.name} | Expire le : {lot.expiration_date}")
            
            # Note d'évolution : Ici, on pourrait ajouter le code pour générer
            # un ticket automatique (mail.activity) au gestionnaire des stocks.
        else:
            _logger.info("INVENTAIRE : Aucun complément alimentaire n'expire à court terme.")