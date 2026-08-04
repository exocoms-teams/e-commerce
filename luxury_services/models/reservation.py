from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LuxuryReservation(models.Model):
    _name = 'luxury.reservation'
    _description = 'Réservation Luxury'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_debut desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('luxury.reservation')
    )
    product_id = fields.Many2one(
        'product.template',
        string='Produit',
        required=True,
        domain="[('type_service', 'in', ['location', 'les_deux'])]"
    )
    client_id = fields.Many2one('res.partner', string='Client')
    client_name = fields.Char(string='Nom du client', required=True)
    client_email = fields.Char(string='Email du client', required=True)
    client_phone = fields.Char(string='Téléphone')

    # Adresse
    client_adresse = fields.Char(string='Adresse')
    client_code_postal = fields.Char(string='Code postal')
    client_pays = fields.Many2one('res.country', string='Pays')

    date_debut = fields.Date(string='Date de début', required=True)
    date_fin = fields.Date(string='Date de fin', required=True)
    nb_jours = fields.Integer(
        string='Nombre de jours',
        compute='_compute_nb_jours',
        store=True
    )
    prix_total = fields.Float(
        string='Prix total (€)',
        compute='_compute_prix_total',
        store=True
    )
    state = fields.Selection([
    ('draft', 'Brouillon'),
    ('en_attente', 'En attente de validation'),
    ('confirmed', 'Confirmée'),
    ('cancelled', 'Annulée'),
     ], string='Statut', default='draft')
    notes = fields.Text(string='Notes')

    @api.depends('date_debut', 'date_fin')
    def _compute_nb_jours(self):
        for rec in self:
            if rec.date_debut and rec.date_fin:
                delta = rec.date_fin - rec.date_debut
                rec.nb_jours = delta.days
            else:
                rec.nb_jours = 0

    @api.depends('nb_jours', 'product_id')
    def _compute_prix_total(self):
        for rec in self:
            if rec.product_id and rec.nb_jours:
                rec.prix_total = rec.nb_jours * rec.product_id.prix_location_jour
            else:
                rec.prix_total = 0

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for rec in self:
            if rec.date_debut and rec.date_fin:
                if rec.date_fin <= rec.date_debut:
                    raise ValidationError(
                        "La date de fin doit être après la date de début !"
                    )
                if rec.product_id and rec.nb_jours < rec.product_id.duree_min_location:
                    raise ValidationError(
                        f"La durée minimum de location est de "
                        f"{rec.product_id.duree_min_location} jours !"
                    )

    @api.constrains('date_debut', 'date_fin', 'product_id')
    def _check_disponibilite(self):
        for rec in self:
            if rec.product_id and rec.date_debut and rec.date_fin:
                chevauchement = self.search([
                    ('product_id', '=', rec.product_id.id),
                    ('state', '=', 'confirmed'),
                    ('id', '!=', rec.id),
                    ('date_debut', '<', rec.date_fin),
                    ('date_fin', '>', rec.date_debut),
                ])
                if chevauchement:
                    raise ValidationError(
                        f"Ce produit est déjà réservé du "
                        f"{chevauchement[0].date_debut} au "
                        f"{chevauchement[0].date_fin} !"
                    )

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            # Envoie email de confirmation au client
            template = self.env.ref(
                'luxury_services.email_template_reservation_confirmed',
                raise_if_not_found=False
            )
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_set_waiting(self):
        for rec in self:
            rec.state = 'en_attente'


    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
            other_confirmed = self.search([
                ('product_id', '=', rec.product_id.id),
                ('state', '=', 'confirmed'),
                ('id', '!=', rec.id),
            ])
            if not other_confirmed:
                rec.product_id.disponible = True
                
                
    def get_payment_url(self):
        """Génère l'URL de paiement pour la réservation"""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/luxury/paiement/{self.id}"