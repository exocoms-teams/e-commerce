# -*- coding: utf-8 -*-
"""Proposition d'une mission à UN artisan, avec délai de réponse (façon Uber)."""
from odoo import fields, models


class SinistreProposition(models.Model):
    _name = 'sinistre.proposition'
    _description = 'Proposition de mission à un artisan'
    _order = 'date_envoi desc, id desc'

    # active=False = proposition d'un tour précédent (après une relance)
    active = fields.Boolean(default=True)
    mission_id = fields.Many2one(
        'sinistre.mission', string='Mission',
        required=True, index=True, ondelete='cascade',
    )
    intervenant_id = fields.Many2one(
        'sinistre.intervenant', string='Artisan',
        required=True, index=True, ondelete='cascade',
    )
    state = fields.Selection([
        ('en_attente', 'En attente'),
        ('accepte', 'Acceptée'),
        ('refuse', 'Refusée'),
        ('expire', 'Expirée'),
        ('annule', 'Annulée'),
    ], string='État', default='en_attente', required=True, index=True)
    date_envoi = fields.Datetime(string='Envoyée le', default=fields.Datetime.now, required=True)
    date_limite = fields.Datetime(string='Limite de réponse', required=True, index=True)
    date_reponse = fields.Datetime(string='Répondue le')
