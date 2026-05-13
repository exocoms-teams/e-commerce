# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SinistrePhoto(models.Model):
    """
    Photos liées à une mission sinistre.
    Avant intervention (obligatoires pour démarrer)
    Après intervention (obligatoires pour clôturer)
    """
    _name = 'sinistre.photo'
    _description = 'Photo Dossier Sinistre'
    _order = 'date_prise desc'

    mission_id = fields.Many2one(
        'sinistre.mission',
        string='Mission',
        required=True,
        ondelete='cascade',
    )
    type_photo = fields.Selection([
        ('avant', 'Avant Intervention'),
        ('pendant', 'Pendant'),
        ('apres', 'Après Intervention'),
    ], string='Type', required=True, default='avant')

    image = fields.Binary(string='Photo', required=True)
    image_filename = fields.Char(string='Nom du fichier')

    description = fields.Char(string='Description')
    date_prise = fields.Datetime(
        string='Date de prise',
        default=fields.Datetime.now,
    )
    intervenant_id = fields.Many2one(
        related='mission_id.intervenant_id',
        string='Intervenant',
        store=True,
    )

    # Géolocalisation (optionnel, envoyé depuis la PWA)
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
