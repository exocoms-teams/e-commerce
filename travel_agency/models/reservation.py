from odoo import models, fields, api

class TravelReservation(models.Model):
    _name = 'travel.reservation'
    _description = 'Travel Reservation'

    name = fields.Char(string='Reference', required=True, default='New')
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
    prix_total = fields.Float(string='Total Price')
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