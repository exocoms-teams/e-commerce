# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_boat_product = fields.Boolean(
        string='Produit bateau',
        default=False,
        help='Cochez cette case pour afficher ce produit dans les pages bateau.',
    )

    boat_category = fields.Selection([
        ('passenger', 'Bateau passagers'),
        ('glass_bottom', 'Bateau à fond transparent'),
        ('yacht', 'Yacht'),
        ('catamaran', 'Catamaran'),
        ('custom', 'Projet sur mesure'),
    ], string='Catégorie bateau', default='passenger')

    boat_service_type = fields.Selection([
        ('sale', 'Vente'),
        ('rental', 'Location'),
        ('quote', 'Sur devis'),
    ], string='Type d’offre', default='quote')

    boat_available = fields.Boolean(string='Disponible', default=True)
    boat_builder = fields.Char(string='Constructeur')
    boat_model = fields.Char(string='Modèle')
    boat_year = fields.Integer(string='Année')
    boat_length = fields.Float(string='Longueur (m)')
    boat_width = fields.Float(string='Largeur (m)')
    boat_capacity = fields.Integer(string='Capacité passagers')
    boat_cabins = fields.Integer(string='Nombre de cabines')
    boat_speed = fields.Float(string='Vitesse max (nœuds)')
    boat_engine = fields.Char(string='Motorisation')
    boat_hull_material = fields.Char(string='Matériau de coque')
    boat_base_port = fields.Char(string='Port / zone de livraison')
    boat_short_description = fields.Text(string='Description courte')
    boat_catalog_url = fields.Char(string='Lien catalogue')
