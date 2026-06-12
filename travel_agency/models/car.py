from odoo import models, fields


class Voiture(models.Model):
    _name = 'travel.car'
    _description = 'Location de voiture'

    name = fields.Char(string='Nom de l\'offre', required=True)
    description = fields.Html(string='Description')
    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920)

    marque = fields.Char(string='Marque')
    modele = fields.Char(string='Modèle')

    categorie = fields.Selection([
        ('economique', 'Économique'),
        ('compacte', 'Compacte'),
        ('berline', 'Berline'),
        ('suv', 'SUV'),
        ('luxe', 'Luxe'),
        ('utilitaire', 'Utilitaire'),
    ], string='Catégorie', default='economique')

    transmission = fields.Selection([
        ('manuelle', 'Manuelle'),
        ('automatique', 'Automatique'),
    ], string='Transmission', default='manuelle')

    nombre_places = fields.Integer(string='Nombre de places', default=5)

    pays = fields.Char(string='Pays')
    ville_prise_en_charge = fields.Char(string='Lieu de prise en charge')
    ville_restitution = fields.Char(string='Lieu de restitution')

    prix_par_jour = fields.Float(string='Prix par jour (€)')
    disponible = fields.Boolean(string='Disponible', default=True)

    points_forts = fields.Text(string='Les plus')
