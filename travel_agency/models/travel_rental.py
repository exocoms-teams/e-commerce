# -*- coding: utf-8 -*-
from odoo import models, fields


class TravelRental(models.Model):
    _name = 'travel.rental'
    _description = 'Maison de Location'
    _order = 'name'

    name            = fields.Char(string='Nom du logement', required=True)
    description     = fields.Html(string='Description')
    image_1920      = fields.Image(string='Image', max_width=1920, max_height=1920)

    # Localisation
    pays            = fields.Char(string='Pays')
    ville           = fields.Char(string='Ville')
    adresse         = fields.Char(string='Adresse')
    latitude        = fields.Float(string='Latitude', digits=(10, 6))
    longitude       = fields.Float(string='Longitude', digits=(10, 6))

    # Caractéristiques
    type_logement   = fields.Selection([
        ('maison',      'Maison'),
        ('villa',       'Villa'),
        ('appartement', 'Appartement'),
        ('chalet',      'Chalet'),
        ('riad',        'Riad'),
        ('bungalow',    'Bungalow'),
    ], string='Type de logement', default='maison')

    nb_chambres     = fields.Integer(string='Chambres', default=1)
    nb_personnes    = fields.Integer(string='Capacité (personnes)', default=2)
    superficie_m2   = fields.Float(string='Superficie (m²)')

    # Équipements (booléens)
    piscine         = fields.Boolean(string='Piscine')
    wifi            = fields.Boolean(string='Wi-Fi')
    parking         = fields.Boolean(string='Parking')
    climatisation   = fields.Boolean(string='Climatisation')
    cuisine_equipee = fields.Boolean(string='Cuisine équipée')
    animaux_admis   = fields.Boolean(string='Animaux admis')

    # Tarif
    prix_par_nuit   = fields.Float(string='Prix par nuit (€)')
    disponible      = fields.Boolean(string='Disponible', default=True)

    points_forts    = fields.Text(string='Points forts')
