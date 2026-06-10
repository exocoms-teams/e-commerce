from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class LuxuryListingRequest(models.Model):
    _name = 'luxury.listing.request'
    _description = 'Demande d\'annonce VIP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        default='Nouveau',
        readonly=True,
    )

    # =========================
    # PROPRIÉTAIRE
    # =========================
    owner_name = fields.Char(
        string='Nom complet',
        required=True,
        tracking=True,
    )
    owner_email = fields.Char(
        string='Email',
        required=True,
        tracking=True,
    )
    owner_phone = fields.Char(
        string='Téléphone',
    )
    owner_country_id = fields.Many2one(
        'res.country',
        string='Pays',
    )
    owner_adresse = fields.Char(
        string='Adresse',
    )

    # =========================
    # TYPE DE BIEN
    # =========================
    type_bien = fields.Selection([
        ('yacht',   'Yacht'),
        ('jet',     'Jet Privé'),
        ('hotel',   'Hôtel / Villa'),
        ('voiture', 'Voiture de Luxe'),
    ], string='Type de bien', required=True, tracking=True)

    # =========================
    # INFORMATIONS DU BIEN
    # =========================
    bien_nom = fields.Char(
        string='Nom / Modèle',
        required=True,
    )
    bien_description = fields.Html(
        string='Description',
    )
    bien_annee = fields.Integer(
        string='Année de fabrication',
    )
    bien_prix_location = fields.Float(
        string='Prix de location / jour (€)',
    )
    bien_prix_vente = fields.Float(
        string='Prix de vente (€)',
    )
    type_service = fields.Selection([
        ('location', 'Location uniquement'),
        ('vente',    'Vente uniquement'),
        ('les_deux', 'Location et Vente'),
    ], string='Type de service', required=True)
    
    
    pays_disponibilite_id = fields.Many2one(
        'res.country',
        string='Pays de disponibilité',
    )
    ville_disponibilite = fields.Char(
        string='Ville / Port / Aéroport',
    )
    zone_navigation = fields.Char(
        string='Zone de navigation / Rayon de déplacement',
        help='Ex: Méditerranée, Europe, Mondial...',
    )
    adresse_disponibilite = fields.Char(
        string='Adresse exacte de disponibilité',
    )
    disponible_des = fields.Date(
        string='Disponible à partir du',
    )

    # --- Yacht ---
    longueur = fields.Float(string='Longueur (m)')
    capacite_personnes = fields.Integer(string='Capacité (personnes)')
    nb_cabines = fields.Integer(string='Nombre de cabines')
    vitesse_croisiere = fields.Float(string='Vitesse de croisière (nœuds)')
    pavillon = fields.Char(string='Pavillon')

    # --- Jet ---
    constructeur_jet = fields.Char(string='Constructeur')
    autonomie_vol = fields.Float(string='Autonomie de vol (h)')
    vitesse_max = fields.Float(string='Vitesse max (km/h)')
    nombre_moteurs = fields.Integer(string='Nombre de moteurs')
    altitude_max = fields.Float(string='Altitude max (m)')
    equipage = fields.Integer(string='Équipage')

    # --- Hôtel / Villa ---
    nb_chambres = fields.Integer(string='Nombre de chambres')
    superficie = fields.Float(string='Superficie (m²)')
    localisation = fields.Char(string='Localisation / Adresse')
    equipements = fields.Text(string='Équipements')

    # --- Voiture ---
    marque = fields.Char(string='Marque')
    modele_voiture = fields.Char(string='Modèle')
    kilometrage = fields.Integer(string='Kilométrage')
    couleur = fields.Char(string='Couleur')

    # =========================
    # PIÈCES JUSTIFICATIVES
    # =========================
    piece_identite = fields.Binary(
        string='Pièce d\'identité',
        required=True,
        attachment=True,
    )
    piece_identite_filename = fields.Char(
        string='Nom fichier identité',
    )
    justif_propriete = fields.Binary(
        string='Justificatif de propriété',
        required=True,
        attachment=True,
    )
    justif_propriete_filename = fields.Char(
        string='Nom fichier propriété',
    )
    photos_bien = fields.Many2many(
        'ir.attachment',
        'listing_attachment_rel',
        'listing_id',
        'attachment_id',
        string='Photos du bien',
    )

    # =========================
    # NOTES ADMIN
    # =========================
    notes_admin = fields.Text(
        string='Notes internes',
    )
    refus_raison = fields.Text(
        string='Raison du refus',
    )

    # =========================
    # PRODUIT CRÉÉ
    # =========================
    product_id = fields.Many2one(
        'product.template',
        string='Produit créé',
        readonly=True,
    )

    # =========================
    # STATUT
    # =========================
    state = fields.Selection([
        ('draft',     'Nouvelle demande'),
        ('review',    'En cours d\'examen'),
        ('approved',  'Approuvée'),
        ('refused',   'Refusée'),
        ('published', 'Publiée'),
    ], string='Statut', default='draft', tracking=True)

    # =========================
    # ACTIONS
    # =========================
    def action_review(self):
        self.write({'state': 'review'})
        
    def action_view_product(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Produit',
            'res_model': 'product.template',
            'res_id': self.product_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_refuse(self):
        self.ensure_one()
        #  Ouvre le wizard au lieu de lever une erreur
        return {
            'type': 'ir.actions.act_window',
            'name': 'Raison du refus',
            'res_model': 'luxury.listing.refuse.wizard',
            'view_mode': 'form',
            'target': 'new',  # popup
            'context': {
                'default_listing_id': self.id,
            },
        }

    def action_approve(self):
        self.write({'state': 'approved'})

        # Logger l'approbation
        self.message_post(
            body=f"""
                <div style="padding: 1rem; background: #f0fff4; border-left: 4px solid #27ae60;">
                    <p><strong> Annonce approuvée</strong></p>
                    <p><strong>Approuvée par :</strong> {self.env.user.name}</p>
                </div>
            """,
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

        self._create_product()

    def action_reset(self):
        self.write({'state': 'draft'})

    # =========================
    # CRÉATION AUTOMATIQUE DU PRODUIT
    # =========================
    def _create_product(self):
        vip_website = self.env['website'].search(
            [('name', '=', 'VIP')], limit=1
        )

        # Mapping catégorie luxe
        categorie_map = {
            'yacht':   'yacht',
            'jet':     'jet',
            'hotel':   'hotel',
            'voiture': 'voiture',
        }

        vals = {
            'name':             self.bien_nom,
            'description_sale': self.bien_description,
            'website_id':       vip_website.id if vip_website else False,
            'is_published':     True,
            'type':             'service',
            'categorie_luxe':   categorie_map.get(self.type_bien, False),
            'type_service':     self.type_service,
            'annee_fabrication': self.bien_annee,
            'disponible':       True,
        }

        # Prix selon type service
        if self.type_service in ('location', 'les_deux'):
            vals['prix_location_jour'] = self.bien_prix_location
            vals['list_price'] = self.bien_prix_location
        if self.type_service in ('vente', 'les_deux'):
            vals['list_price'] = self.bien_prix_vente

        # Champs spécifiques par type
        if self.type_bien == 'yacht':
            vals.update({
                'longueur':          self.longueur,
                'capacite_personnes': self.capacite_personnes,
                'nb_cabines':        self.nb_cabines,
                'vitesse_croisiere': self.vitesse_croisiere,
                'pavillon':          self.pavillon,
                'localisation': f"{self.ville_disponibilite or ''} - {self.pays_disponibilite_id.name or ''}".strip(' -'),
            })
        elif self.type_bien == 'jet':
            vals.update({
                'constructeur_jet': self.constructeur_jet,
                'autonomie_vol':    self.autonomie_vol,
                'vitesse_max':      self.vitesse_max,
                'nombre_moteurs':   self.nombre_moteurs,
                'altitude_max':     self.altitude_max,
                'equipage':         self.equipage,
                'localisation': f"{self.ville_disponibilite or ''} - {self.pays_disponibilite_id.name or ''}".strip(' -'),
            })

        product = self.env['product.template'].sudo().create(vals)

        # Transférer les photos
        if self.photos_bien:
            for attachment in self.photos_bien:
                attachment.write({
                    'res_model': 'product.template',
                    'res_id':    product.id,
                })

        self.write({
            'product_id': product.id,
            'state':      'published',
        })

        self._send_approval_email(product)

        _logger.info(
            'Produit %s créé depuis la demande %s',
            product.name, self.name
        )

        return product

    # =========================
    # EMAILS
    # =========================
    def _send_approval_email(self, product):
        template = self.env.ref(
            'luxury_services.email_template_listing_approved',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=True)

    def _send_refusal_email(self):
        template = self.env.ref(
            'luxury_services.email_template_listing_refused',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=True)

    # =========================
    # SÉQUENCE
    # =========================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'luxury.listing.request'
                ) or 'Nouveau'
        return super().create(vals_list)