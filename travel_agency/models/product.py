from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type_voyage = fields.Selection([
        ('aller_simple', 'Aller simple'),
        ('aller_retour', 'Aller-retour'),
        ('circuit', 'Circuit touristique'),
        ('sejour', 'Séjour'),
    ], string='Type de voyage', default='aller_retour')

    categorie_voyage = fields.Selection([
        ('vol', 'Vol'),
        ('hotel', 'Hôtel'),
        ('package', 'Package Vol + Hôtel'),
        ('circuit', 'Circuit'),
    ], string='Catégorie', default='package')

    pays_depart = fields.Char(string='Pays de départ')
    ville_depart = fields.Char(string='Ville de départ')
    pays_destination = fields.Char(string='Pays destination')
    ville_destination = fields.Char(string='Ville destination')

    duree_jours = fields.Integer(string='Durée (jours)', default=1)
    nombre_personnes_max = fields.Integer(string='Capacité max (personnes)')
    classe_voyage = fields.Selection([
        ('economique', 'Économique'),
        ('affaires', 'Affaires'),
        ('premiere', 'Première classe'),
    ], string='Classe', default='economique')

    prix_par_personne = fields.Float(string='Prix par personne (€)')
    disponible = fields.Boolean(string='Disponible', default=True)

    def is_available_for_dates(self, date_debut, date_fin):
        self.ensure_one()
        reservations = self.env['travel.reservation'].search([
            ('product_id', '=', self.id),
            ('state', '=', 'confirmed'),
            ('date_depart', '<', date_fin),
            ('date_retour', '>', date_debut),
        ])
        return len(reservations) == 0