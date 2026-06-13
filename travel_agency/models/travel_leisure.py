# -*- coding: utf-8 -*-
from odoo import models, fields


class TravelLeisure(models.Model):
    _name = 'travel.leisure'
    _description = 'Groupe de Sorties et Loisirs'
    _order = 'name'

    name            = fields.Char(string='Nom de l\'activité', required=True)
    description     = fields.Html(string='Description')
    image_1920      = fields.Image(string='Image', max_width=1920, max_height=1920)

    # Catégorie
    categorie       = fields.Selection([
        ('sport',       'Sport & Aventure'),
        ('culture',     'Culture & Patrimoine'),
        ('gastronomie', 'Gastronomie'),
        ('nature',      'Nature & Randonnée'),
        ('bien_etre',   'Bien-être & Spa'),
        ('famille',     'Famille'),
        ('soiree',      'Soirée & Événement'),
    ], string='Catégorie', required=True)

    # Lieu
    pays            = fields.Char(string='Pays')
    ville           = fields.Char(string='Ville')

    # Détails
    duree_heures    = fields.Float(string='Durée (heures)')
    nb_personnes_min = fields.Integer(string='Groupe minimum', default=1)
    nb_personnes_max = fields.Integer(string='Groupe maximum')
    niveau          = fields.Selection([
        ('tous',        'Tous niveaux'),
        ('debutant',    'Débutant'),
        ('intermediaire','Intermédiaire'),
        ('avance',      'Avancé'),
    ], string='Niveau requis', default='tous')

    # Tarif
    prix_par_personne = fields.Float(string='Prix par personne (€)')
    disponible      = fields.Boolean(string='Disponible', default=True)

    points_forts    = fields.Text(string='Points forts')
