from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Type de service
    type_service = fields.Selection([
        ('vente', 'À vendre'),
        ('location', 'À louer'),
        ('les_deux', 'Vente et Location'),
    ], string='Type de service', default='vente')

    # Catégorie de luxe
    categorie_luxe = fields.Selection([
        ('yacht', 'Yacht'),
        ('jet', 'Jet Privé'),
        ('vip', 'Conciergerie VIP'),
    ], string='Catégorie Luxe', default='yacht')

    # Caractéristiques
    longueur = fields.Float(string='Longueur (m)')
    capacite_personnes = fields.Integer(string='Capacité (personnes)')
    duree_min_location = fields.Integer(string='Durée minimum location (jours)', default=1)
    prix_location_jour = fields.Float(string='Prix location / jour (€)')

    # Disponibilité
    disponible = fields.Boolean(string='Disponible à la location', default=True)

    def is_available_for_dates(self, date_debut, date_fin):
        """Vérifie si le produit est disponible pour les dates données"""
        self.ensure_one()
        reservations = self.env['luxury.reservation'].search([
            ('product_id', '=', self.id),
            ('state', '=', 'confirmed'),
            ('date_debut', '<', date_fin),
            ('date_fin', '>', date_debut),
        ])
        return len(reservations) == 0