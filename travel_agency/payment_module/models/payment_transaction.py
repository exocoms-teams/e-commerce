from odoo import models, fields, api

class TravelPaymentTransaction(models.Model):
    _name = 'travel.payment.transaction'
    _description = 'Travel Payment Transaction'

    name = fields.Char(string='Référence transaction', required=True, default='New')
    reservation_id = fields.Many2one('travel.reservation', string='Réservation')
    provider_id = fields.Many2one('travel.payment.provider', string='Prestataire de paiement')
    amount = fields.Float(string='Montant', related='reservation_id.prix_total', store=True)
    commission = fields.Float(string='Commission', related='reservation_id.commission_amount', store=True)
    currency = fields.Selection([
        ('EUR', 'Euro €'),
        ('USD', 'Dollar $'),
        ('DZD', 'Dinar DZD'),
    ], string='Devise', default='EUR')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('pending', 'En attente'),
        ('done', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft')
    date_transaction = fields.Datetime(string='Date de transaction')
    notes = fields.Text(string='Notes')
    first_name = fields.Char(string='Prénom')
    last_name = fields.Char(string='Nom')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Téléphone')
    address = fields.Char(string='Adresse')
    city = fields.Char(string='Ville')
    zip_code = fields.Char(string='Code Postal')
    card_last_4 = fields.Char(string='4 derniers chiffres carte')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('travel.payment.transaction') or 'New'
        return super().create(vals_list)

    def action_pending(self):
        for rec in self:
            rec.state = 'pending'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.date_transaction = fields.Datetime.now()

    def action_failed(self):
        for rec in self:
            rec.state = 'failed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_reset(self):
        for rec in self:
            rec.state = 'draft'