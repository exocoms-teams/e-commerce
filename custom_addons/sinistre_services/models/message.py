# -*- coding: utf-8 -*-
"""
message.py — Messagerie interne sur les missions
Permet à l'assurance, l'artisan et la plateforme d'échanger sur une mission.
"""
from odoo import api, fields, models


class SinistreMessage(models.Model):
    _name        = 'sinistre.message'
    _description = 'Message Mission'
    _order       = 'date_envoi asc'

    mission_id  = fields.Many2one('sinistre.mission', required=True, ondelete='cascade', index=True)
    auteur_type = fields.Selection([
        ('plateforme', 'Plateforme'),
        ('assurance',  'Assurance'),
        ('artisan',    'Artisan'),
        ('client',     'Client'),
    ], string='De', required=True, default='plateforme')
    auteur_nom  = fields.Char(string='Nom expéditeur')
    contenu     = fields.Text(string='Message', required=True)
    date_envoi  = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    lu_artisan  = fields.Boolean(default=False)
    lu_assurance = fields.Boolean(default=False)
    piece_jointe = fields.Binary(string='Pièce jointe')
    piece_jointe_nom = fields.Char(string='Nom fichier')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.auteur_type in ('assurance', 'plateforme') and rec.mission_id.intervenant_id:
                rec._push_to_artisan()
        return records

    @api.model
    def _push_notification(self, token, title, body, data=None, data_only=False):
        """Envoie une notification FCM à un token donné."""
        try:
            import requests
            server_key = self.env['ir.config_parameter'].sudo().get_param('sinistre.fcm_server_key', '')
            if not server_key or not token:
                return
            payload = {
                'to': token,
                'data': {k: str(v) for k, v in (data or {}).items()},
            }
            if data_only:
                payload['data']['title'] = title or ''
                payload['data']['body'] = body or ''
                payload['priority'] = 'high'
            else:
                payload['notification'] = {'title': title, 'body': body}
            requests.post(
                'https://fcm.googleapis.com/fcm/send',
                json=payload,
                headers={'Authorization': f'key={server_key}'},
                timeout=5,
            )
        except Exception:
            pass

    def _push_to_artisan(self):
        """Envoie une notification push FCM à l'artisan."""
        iv = self.mission_id.intervenant_id
        if not iv or not hasattr(iv, 'fcm_token') or not iv.fcm_token:
            return
        try:
            import requests
            from odoo import tools
            server_key = self.env['ir.config_parameter'].sudo().get_param('sinistre.fcm_server_key', '')
            if not server_key:
                return
            requests.post(
                'https://fcm.googleapis.com/fcm/send',
                json={
                    'to': iv.fcm_token,
                    'notification': {
                        'title': f"Nouveau message — {self.mission_id.reference}",
                        'body':  self.contenu[:100],
                    },
                    'data': {
                        'type':       'new_message',
                        'mission_id': str(self.mission_id.id),
                    },
                },
                headers={'Authorization': f'key={server_key}'},
                timeout=5,
            )
        except Exception:
            pass
