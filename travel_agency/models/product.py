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
        """Vérifie si le produit est disponible pour des dates données.
        Accepte des dates en objet date ou en chaîne 'YYYY-MM-DD'."""
        self.ensure_one()

        # Normaliser les dates en chaînes 'YYYY-MM-DD' pour la recherche
        try:
            if not date_debut or not date_fin:
                return True
            start = date_debut if isinstance(date_debut, str) else fields.Date.to_string(date_debut)
            end = date_fin if isinstance(date_fin, str) else fields.Date.to_string(date_fin)
        except Exception:
            # Si la conversion échoue, considérer disponible pour éviter blocage
            return True

        # Rechercher les réservations confirmées qui chevauchent la période
        try:
            reservations = self.env['travel.reservation'].search([
                ('product_id', '=', self.id),
                ('state', '=', 'confirmed'),
                ('date_depart', '<', end),
                ('date_retour', '>', start),
            ])
            return len(reservations) == 0
        except Exception:
            return True
