# -*- coding: utf-8 -*-
"""
assurance_portal.py — Portail web pour les compagnies d'assurance
Inscription, gestion des missions, messagerie, annulation.
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import secrets


class SinistreAssurance(models.Model):
    _inherit = 'sinistre.assurance'

    # Compte portail
    portal_user_id   = fields.Many2one('res.users', string='Compte Portail', readonly=True)
    inscription_date = fields.Datetime(string="Date d'inscription", readonly=True)
    statut_compte    = fields.Selection([
        ('en_attente', 'En attente de validation'),
        ('actif',      'Actif'),
        ('suspendu',   'Suspendu'),
    ], default='en_attente', string='Statut compte', tracking=True)

    # Paramètres annulation
    peut_annuler     = fields.Boolean(string='Peut annuler des missions', default=True)
    delai_annulation = fields.Integer(string="Délai max annulation (h)", default=2,
                                       help="Délai en heures avant RDV après lequel l'annulation est facturée")

    def action_valider_compte(self):
        """Valide le compte assurance et crée le portail utilisateur."""
        self.ensure_one()
        if not self.portal_user_id:
            self._creer_compte_portail()
        self.write({'statut_compte': 'actif'})
        self.message_post(body=f"Compte assurance activé — clé API générée")

    def _creer_compte_portail(self):
        """Crée un compte utilisateur portail pour l'assurance."""
        if not self.partner_id.email:
            raise UserError("L'assurance doit avoir un email pour créer un compte portail.")
        group_portal = self.env.ref('base.group_portal')
        user = self.env['res.users'].create({
            'name':       self.name,
            'login':      self.partner_id.email,
            'partner_id': self.partner_id.id,
            'groups_id':  [(4, group_portal.id)],
            'password':   secrets.token_urlsafe(12),
        })
        # Générer la clé API
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(32)
        self.write({
            'portal_user_id':   user.id,
            'inscription_date': fields.Datetime.now(),
        })
        return user

    def action_suspendre(self):
        self.write({'statut_compte': 'suspendu'})
        if self.portal_user_id:
            self.portal_user_id.write({'active': False})

    def _check_annulation_autorisee(self, mission):
        """Vérifie si l'assurance peut encore annuler sans frais."""
        if not mission.date_rdv:
            return True, 0
        from datetime import datetime
        delta = (mission.date_rdv - datetime.now()).total_seconds() / 3600
        if delta < self.delai_annulation:
            return False, self.delai_annulation
        return True, delta
