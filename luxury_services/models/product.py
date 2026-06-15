from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    is_luxury_product = fields.Boolean(
        string='Est un produit Luxury',
        compute='_compute_is_luxury_product',
        store=False,
    )

    @api.depends('website_id')
    def _compute_is_luxury_product(self):
        vip_website = self.env['website'].search(
            [('name', '=', 'VIP')], limit=1
        )
        for record in self:
            record.is_luxury_product = (
                vip_website and record.website_id.id == vip_website.id
            )

    
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
    
    
    localisation = fields.Char(
        string='Localisation'
    )

    # Caractéristiques yacht
    longueur = fields.Float(string='Longueur (m)')
    capacite_personnes = fields.Integer(string='Capacité (personnes)')
    duree_min_location = fields.Integer(string='Durée minimum location (jours)', default=1)
    nb_cabines = fields.Integer(string='Nombre de cabines')
    vitesse_croisiere = fields.Float(string='Vitesse maximale (nœuds)')
    annee_fabrication = fields.Integer(string='Année de fabrication')
    pavillon = fields.Char(string='Pavillon (nationalité)')

    # Informations Jet privé
    constructeur_jet = fields.Char(string='Constructeur')
    modele_jet = fields.Char(string='Modèle du jet')
    autonomie_vol = fields.Float(string='Autonomie de vol (km)')
    vitesse_max = fields.Float(string='Vitesse max (km/h)')
    nombre_moteurs = fields.Integer(string='Nombre de moteurs')
    altitude_max = fields.Float(string='Altitude max (m)')
    equipage = fields.Integer(string='Nombre équipage')    
    
    prix_location_jour = fields.Float(string='Prix location / jour (€)')
    # Disponibilité
    disponible = fields.Boolean(string='Disponible à la location', default=True)

    destination_ids = fields.Many2many(
    'luxury.destination',
    'product_luxury_destination_rel',
    'product_id',
    'destination_id',
    string='Destinations disponibles',
    )

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