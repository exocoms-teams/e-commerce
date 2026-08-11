# -*- coding: utf-8 -*-
from odoo import models, api, fields
from datetime import timedelta

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def signup(self, values, token=None):
        """Surcharge : Un client s'inscrit, on réveille le système s'il dormait."""
        res = super(ResUsers, self).signup(values, token)
        
        # On récupère le Cron
        cron = self.env.ref('exocoms_signup_verify.ir_cron_purge_unconfirmed_signups', raise_if_not_found=False)
        
        # Si c'est le premier client (cron éteint), on l'allume pour dans 15 minutes
        if cron and not cron.active:
            cron.sudo().write({
                'active': True,
                'nextcall': fields.Datetime.now() + timedelta(minutes=15)
            })
            
        return res

    @api.model
    def _cron_purge_unconfirmed_signups(self):
        """Le Cron se réveille, nettoie, et calcule l'heure exacte de son prochain réveil."""
        now = fields.Datetime.now()
        limit_date = now - timedelta(minutes=15)
        
        # 1. On supprime ceux dont les 15 minutes sont écoulées
        expired_users = self.search([
            ('state', '=', 'new'), 
            ('create_date', '<', limit_date)
        ])
        if expired_users:
            expired_users.unlink()
            
        # 2. On cherche LE PROCHAIN client dans la file d'attente
        next_user_in_queue = self.search([('state', '=', 'new')], order='create_date asc', limit=1)
        
        cron = self.env.ref('exocoms_signup_verify.ir_cron_purge_unconfirmed_signups', raise_if_not_found=False)
        if cron:
            if next_user_in_queue:
                # Il reste un client dans la file ! 
                # On calcule l'heure exacte de la fin de ses 15 minutes
                exact_expiration_time = next_user_in_queue.create_date + timedelta(minutes=15)
                
                # On programme le prochain réveil du Cron EXACTEMENT à cette seconde-là
                cron.write({
                    'active': True,
                    'nextcall': exact_expiration_time
                })
            else:
                # La file d'attente est vide. Le Cron s'éteint totalement.
                cron.write({'active': False})