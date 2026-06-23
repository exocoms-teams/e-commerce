# -*- coding: utf-8 -*-
"""Suivi des réponses aux propositions de mission (acceptée / refusée)."""
from odoo import fields, models


class SinistrePropositionReponse(models.Model):
    _name = 'sinistre.proposition.reponse'
    _description = 'Réponse à une proposition de mission'
    _order = 'date_reponse desc'

    intervenant_id = fields.Many2one(
        'sinistre.intervenant', required=True, index=True, ondelete='cascade',
    )
    mission_id = fields.Many2one(
        'sinistre.mission', required=True, index=True, ondelete='cascade',
    )
    reponse = fields.Selection([
        ('accepte', 'Acceptée'),
        ('refuse', 'Refusée'),
    ], string='Réponse', required=True)
    date_reponse = fields.Datetime(
        string='Date', default=fields.Datetime.now, required=True, index=True,
    )

    _sql_constraints = [
        (
            'unique_reponse_intervenant_mission',
            'unique(intervenant_id, mission_id)',
            'Une seule réponse par mission et intervenant.',
        ),
    ]
