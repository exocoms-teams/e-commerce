from odoo import models, fields


class Train(models.Model):
    _name = 'travel.train'
    _description = 'Train'

    name = fields.Char(string='Nom du trajet', required=True)
    description = fields.Html(string='Description')
    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920)

    compagnie = fields.Char(string='Compagnie ferroviaire')
    numero_train = fields.Char(string='Numéro de train')

    pays_depart = fields.Char(string='Pays de départ')
    ville_depart = fields.Char(string='Ville de départ')
    gare_depart = fields.Char(string='Gare de départ')

    pays_arrivee = fields.Char(string='Pays d\'arrivée')
    ville_arrivee = fields.Char(string='Ville d\'arrivée')
    gare_arrivee = fields.Char(string='Gare d\'arrivée')

    classe = fields.Selection([
        ('seconde', 'Seconde classe'),
        ('premiere', 'Première classe'),
    ], string='Classe', default='seconde')

    duree_heures = fields.Float(string='Durée (heures)')
    prix = fields.Float(string='Prix (€)')
    disponible = fields.Boolean(string='Disponible', default=True)

    points_forts = fields.Text(string='Les plus')
