# models/tracker_cron_log.py
"""WIN-83 : journalisation des exécutions des scripts de collecte.

Objectif : pouvoir diagnostiquer rapidement quel script a échoué et
pourquoi, sans relire les logs serveur bruts.

Contrainte du ticket : la journalisation ne doit jamais faire échouer un
script de collecte. Le point d'entrée `log_execution` est donc pensé pour
être appelé en best-effort, encapsulé dans un try/except côté appelant
(voir collecte_scrapers/ebay_ingestor.py et meta_ingestor.py).
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class TrackerCronLog(models.Model):
    _name = 'tracker.cron.log'
    _description = "Journal d'exécution des scripts de collecte (WIN-83)"
    _order = 'execution_date desc'

    cron_name = fields.Char(string='Script', required=True)
    execution_date = fields.Datetime(string="Date d'exécution", default=fields.Datetime.now, required=True)
    status = fields.Selection([
        ('success', 'Succès'),
        ('error', 'Erreur'),
    ], string='Statut', required=True)
    message = fields.Text(string='Message')

    @api.model
    def log_execution(self, cron_name, status, message=None):
        """Point d'entrée best-effort utilisé par les scripts de collecte.

        Ne lève jamais d'exception : une erreur de journalisation ne doit
        pas interrompre le script appelant (contrainte explicite du
        ticket WIN-83). En cas d'échec d'écriture, l'erreur est seulement
        journalisée dans les logs serveur standard.
        """
        try:
            self.sudo().create({
                'cron_name': cron_name,
                'status': status,
                'message': message,
            })
        except Exception:
            _logger.exception(
                "WIN-83: échec de la journalisation pour le script %s", cron_name
            )
