# -*- coding: utf-8 -*-
from odoo import models, fields

class PlanetReview(models.Model):
    _name = 'planet.review'
    _description = 'Avis clients Planet Mobil'
    _order = 'date desc'

    name = fields.Char(string='Nom', required=True)
    rating = fields.Integer(string='Note', default=5)
    product = fields.Char(string='Produit acheté', required=False)
    comment = fields.Text(string='Commentaire', required=True)
    date = fields.Date(string='Date', default=fields.Date.today)
    is_published = fields.Boolean(string='Publié', default=False)

