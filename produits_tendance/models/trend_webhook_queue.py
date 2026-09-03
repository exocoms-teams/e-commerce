# models/trend_webhook_queue.py
"""WIN-67 : file d'attente légère pour les webhooks d'alerte (Slack/Telegram).

Pas d'addon `queue_job` disponible sur cette instance (vérifié sur le code
source Odoo.sh : absent de /home/odoo/src). Alternative explicitement
autorisée par le ticket ("ou différer l'exécution") : un modèle de file
d'attente traité par un ir.cron, plutôt qu'un appel HTTP synchrone dans le
thread de sauvegarde du score.
"""
import logging

import requests
from odoo import fields, models

_logger = logging.getLogger(__name__)

WEBHOOK_TIMEOUT_SECONDS = 10


class TrendWebhookQueue(models.Model):
    _name = 'trend.webhook.queue'
    _description = "File d'attente des webhooks d'alerte de score (WIN-67)"
    _order = 'create_date asc'

    url = fields.Char(required=True)
    payload = fields.Text(required=True, help="Corps JSON de la requête POST.")
    product_id = fields.Many2one('trend.product', ondelete='cascade')
    state = fields.Selection([
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
    ], default='pending', required=True, index=True)
    error_message = fields.Text()

    def _cron_process_pending(self, batch_size=50):
        """Traite les webhooks en attente. Appelé par un ir.cron (WIN-67) —
        c'est ici, hors du thread de sauvegarde du trend.score, que l'appel
        HTTP bloquant a lieu."""
        pending = self.search([('state', '=', 'pending')], limit=batch_size)
        for job in pending:
            try:
                response = requests.post(
                    job.url,
                    data=job.payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=WEBHOOK_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                job.write({'state': 'sent', 'error_message': False})
            except Exception as exc:
                _logger.warning("WIN-67: échec envoi webhook %s: %s", job.id, exc)
                job.write({'state': 'failed', 'error_message': str(exc)})
