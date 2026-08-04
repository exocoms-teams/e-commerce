# models/trend_score_alert.py
"""WIN-67 : alertes de dépassement de seuil (email pour les abonnés
Standard, webhook Slack/Telegram pour les abonnés Pro).

Point d'accroche choisi : `trend.score.create()`, plutôt qu'une surcharge du
compute `_compute_current_score` de trend_product.py. Raisons :
- La création d'un trend.score est l'événement précis et non ambigu de
  "le score vient d'être mis à jour" — un compute peut se redéclencher pour
  d'autres raisons (invalidation de cache) sans qu'un nouveau score existe.
- Ça évite de modifier la logique de calcul de trend_product.py (WIN-25/ZC)
  pour une fonctionnalité qui n'a rien à voir avec le calcul lui-même.

Seuil et URL de webhook : System Parameters (`ir.config_parameter`), même
pattern que `winners.api_key` déjà utilisé dans ce module. Choix fait sans
confirmation explicite de l'équipe — à valider :
- `produits_tendance.score_alert_threshold` : seuil global, un seul webhook
  d'entreprise (Slack/Telegram) notifié par franchissement, pas un webhook
  par utilisateur Pro (cohérent avec le "B2B Push Notification" de l'objectif).
- `produits_tendance.webhook_url` : URL du webhook Slack/Telegram.
"""
import json

from odoo import api, models


class TrendScore(models.Model):
    _inherit = 'trend.score'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.sudo()._winners_check_score_alerts()
        return records

    def _winners_check_score_alerts(self):
        threshold = self.env['ir.config_parameter'].sudo().get_param(
            'produits_tendance.score_alert_threshold'
        )
        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            return  # Pas de seuil configuré : pas d'alerte.

        for score in self:
            if score.computed_score < threshold:
                continue
            score._winners_notify_standard_users()
            score._winners_queue_pro_webhook()

    def _winners_notify_standard_users(self):
        """Email via mail.mail.create() pour les abonnés Standard (pas Pro,
        qui reçoivent le webhook à la place — canaux différenciés par tier).
        create() suffit : mail.mail est déjà mis en file d'attente sortante
        par Odoo (state='outgoing'), pas d'envoi synchrone ici."""
        standard_group = self.env.ref('produits_tendance.group_trend_standard')
        pro_group = self.env.ref('produits_tendance.group_trend_pro')
        standard_users = self.env['res.users'].search([
            ('group_ids', 'in', standard_group.id),
            ('group_ids', 'not in', pro_group.id),
        ])

        for user in standard_users:
            if not user.email:
                continue
            self.env['mail.mail'].create({
                'subject': f"🚀 {self.product_id.name} dépasse le seuil de tendance",
                'body_html': (
                    f"<p>Le produit <strong>{self.product_id.name}</strong> vient "
                    f"d'atteindre un score de tendance de "
                    f"<strong>{self.computed_score:.1f}</strong>.</p>"
                ),
                'email_to': user.email,
                'email_from': self.env.company.email or 'winners@exocoms.fr',
            })

    def _winners_queue_pro_webhook(self):
        """Ne fait pas d'appel HTTP direct : dépose une entrée dans
        trend.webhook.queue, traitée plus tard par le cron WIN-67, pour ne
        jamais bloquer le thread de sauvegarde du score (contrainte du ticket)."""
        webhook_url = self.env['ir.config_parameter'].sudo().get_param(
            'produits_tendance.webhook_url'
        )
        if not webhook_url:
            return

        self.env['trend.webhook.queue'].create({
            'url': webhook_url,
            'payload': json.dumps({
                'text': (
                    f"🚀 {self.product_id.name} dépasse le seuil de tendance "
                    f"(score: {self.computed_score:.1f})"
                ),
            }),
            'product_id': self.product_id.id,
        })
