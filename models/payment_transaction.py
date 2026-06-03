# -*- coding: utf-8 -*-
from odoo import models, fields


class PaymentTransaction(models.Model):
    _name = 'payment.transaction'
    _description = 'Payment Transaction'
    _order = 'create_date DESC'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    amount = fields.Float(string='Amount', required=True, digits=(10, 2))
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    zip_code = fields.Char(string='Zip Code')
    card_last_4 = fields.Char(string='Card Last 4 Digits', size=4)
    payment_date = fields.Datetime(string='Payment Date', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ], string='Status', default='pending', required=True)
    notes = fields.Text(string='Notes')

    def action_mark_completed(self):
        self.write({'status': 'completed'})

    def action_mark_failed(self):
        self.write({'status': 'failed'})

    def action_refund(self):
        self.write({'status': 'refunded'})
