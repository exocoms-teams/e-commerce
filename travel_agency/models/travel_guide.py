# -*- coding: utf-8 -*-
from odoo import models, fields


class TravelGuide(models.Model):
    _name = 'travel.guide'
    _description = 'Guide Touristique'
    _order = 'name'

    name            = fields.Char(string='Nom du guide', required=True)
    description     = fields.Html(string='Description')
    image_1920      = fields.Image(string='Photo', max_width=1920, max_height=1920)

    # Identité
    prenom          = fields.Char(string='Prénom')
    specialite      = fields.Char(string='Spécialité', help='Ex: Histoire, Nature, Gastronomie')
    langues         = fields.Char(string='Langues parlées', help='Ex: Français, Anglais, Arabe')
    experience_ans  = fields.Integer(string='Années d\'expérience')
    note            = fields.Float(string='Note (/5)', digits=(2, 1))

    # Zone d'activité
    pays            = fields.Char(string='Pays')
    ville           = fields.Char(string='Ville / Région')

    # Tarif
    prix_par_jour   = fields.Float(string='Prix par jour (€)')
    disponible      = fields.Boolean(string='Disponible', default=True)

    # Contact
    email           = fields.Char(string='Email')
    telephone       = fields.Char(string='Téléphone')

    points_forts    = fields.Text(string='Points forts')
