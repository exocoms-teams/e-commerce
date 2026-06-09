from odoo import models, fields, api

class TravelReservation(models.Model):
    _name = 'travel.reservation'
    _description = 'Travel Reservation'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    client_name = fields.Char(string='Client Name', required=True)
    client_email = fields.Char(string='Email')
    client_phone = fields.Char(string='Phone')
    client_country = fields.Char(string='Country')
    product_id = fields.Many2one('product.template', string='Travel Package')
    date_depart = fields.Date(string='Departure Date')
    date_retour = fields.Date(string='Return Date')
    nb_jours = fields.Integer(string='Duration', compute='_compute_duration', store=True)
    nb_adultes = fields.Integer(string='Adults', default=1)
    nb_enfants = fields.Integer(string='Children', default=0)
    nb_voyageurs = fields.Integer(string='Total Travelers', compute='_compute_total', store=True)
    prix_total = fields.Float(string='Total Price', compute='_compute_prix_total', store=True)
    payment_provider_id = fields.Many2one('travel.payment.provider', string='Payment Provider')
    commission_amount = fields.Float(string='Commission Amount', compute='_compute_commission', store=True)
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('en_attente', 'Waiting'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], default='draft')

    @api.depends('date_depart', 'date_retour')
    def _compute_duration(self):
        for rec in self:
            if rec.date_depart and rec.date_retour:
                rec.nb_jours = (rec.date_retour - rec.date_depart).days
            else:
                rec.nb_jours = 0

    @api.depends('nb_adultes', 'nb_enfants')
    def _compute_total(self):
        for rec in self:
            rec.nb_voyageurs = rec.nb_adultes + rec.nb_enfants

    @api.depends('nb_voyageurs', 'product_id')
    def _compute_prix_total(self):
        for rec in self:
            if rec.product_id and rec.nb_voyageurs:
                rec.prix_total = rec.nb_voyageurs * rec.product_id.prix_par_personne
            else:
                rec.prix_total = 0.0

    @api.depends('prix_total', 'payment_provider_id')
    def _compute_commission(self):
        for rec in self:
            if rec.payment_provider_id and rec.prix_total:
                rec.commission_amount = rec.prix_total * (rec.payment_provider_id.commission_rate / 100)
            else:
                rec.commission_amount = 0.0

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('travel.reservation') or 'New'
        return super().create(vals)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            template = self.env.ref(
                'travel_agency.email_template_reservation_confirmed',
                raise_if_not_found=False
            )
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_waiting(self):
        for rec in self:
            rec.state = 'en_attente'

    def action_reset(self):
        for rec in self:
            rec.state = 'draft'