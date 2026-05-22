# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PlanetProduct(models.Model):
    _name = 'planet.product'
    _description = 'Produit TechShop Pro'
    _order = 'sequence, name'

    name = fields.Char(string='Nom du produit', required=True)
    category = fields.Char(string='Categorie', required=False)       #manquant 
    brand = fields.Char(string='Marque', required=False)           #manquant
    color = fields.Char(string='Couleur', required=False)          #manquant  
    specs = fields.Char(string='Caracteristiques', required=False)
    description = fields.Text(string='Description')
    price = fields.Float(string='Prix (€)', required=True, default=0.0)
    rating = fields.Float(string='Note', default=5.0)
    image = fields.Binary(string='Image', attachment=True)
    image_url = fields.Char(string='URL Image externe')
    badge = fields.Char(string='Badge (ex: Nouveau, Promo)')
    is_top_vente = fields.Boolean(string='Top Vente', default=False)
    is_nouveaute = fields.Boolean(string='Nouveauté', default=False)
    sequence = fields.Integer(string='Ordre', default=10)
    active = fields.Boolean(string='Actif', default=True)

    @api.depends('rating')
    def _compute_stars(self):
        for rec in self:
            rec.stars_filled = int(rec.rating)
            rec.stars_empty = 5 - int(rec.rating)

    stars_filled = fields.Integer(compute='_compute_stars', string='Étoiles pleines')
    stars_empty = fields.Integer(compute='_compute_stars', string='Étoiles vides')
