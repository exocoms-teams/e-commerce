from odoo import models, fields


class Vol(models.Model):
    _name = 'travel.vol'
    _description = 'Vol'

    name = fields.Char(string='Nom du vol', required=True)
    description = fields.Html(string='Description')
    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920)

    compagnie = fields.Char(string='Compagnie aérienne')
    numero_vol = fields.Char(string='Numéro de vol')

    pays_depart = fields.Char(string='Pays de départ')
    ville_depart = fields.Char(string='Ville de départ')
    aeroport_depart = fields.Char(string='Aéroport de départ')

    pays_arrivee = fields.Char(string='Pays d\'arrivée')
    ville_arrivee = fields.Char(string='Ville d\'arrivée')
    aeroport_arrivee = fields.Char(string='Aéroport d\'arrivée')

    type_vol = fields.Selection([
        ('aller_simple', 'Aller simple'),
        ('aller_retour', 'Aller-retour'),
    ], string='Type de vol', default='aller_retour')

    classe = fields.Selection([
        ('economique', 'Économique'),
        ('affaires', 'Affaires'),
        ('premiere', 'Première classe'),
    ], string='Classe', default='economique')

    duree_heures = fields.Float(string='Durée (heures)')
    prix = fields.Float(string='Prix (€)')
    disponible = fields.Boolean(string='Disponible', default=True)

    points_forts = fields.Text(string='Les plus')
