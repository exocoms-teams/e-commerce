from odoo import models, fields, api

class TravelPaymentTransaction(models.Model):
    _name = 'travel.payment.transaction'
    _description = 'Travel Payment Transaction'

    name = fields.Char(string='Transaction Reference', required=True, default='New')
    reservation_id = fields.Many2one('travel.reservation', string='Reservation', required=True)
    provider_id = fields.Many2one('travel.payment.provider', string='Payment Provider', required=True)
    amount = fields.Float(string='Amount', related='reservation_id.prix_total', store=True)
    commission = fields.Float(string='Commission', related='reservation_id.commission_amount', store=True)
    currency = fields.Selection([
        ('EUR', 'Euro €'),
        ('USD', 'Dollar $'),
        ('DZD', 'Dinar DZD'),
    ], string='Currency', default='EUR')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    date_transaction = fields.Datetime(string='Transaction Date')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('travel.payment.transaction') or 'New'
        return super().create(vals)

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