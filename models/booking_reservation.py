# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import datetime, timedelta


class Booking(models.Model):
    _name = 'booking.reservation'
    _description = 'Booking Reservation'
    _order = 'date_start DESC'

    name = fields.Char(string='Reservation Number', readonly=True, copy=False)
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    date_start = fields.Datetime(string='Reservation Date', required=True)
    date_end = fields.Datetime(string='End Date')
    service = fields.Selection([
        ('consultation', 'Consultation'),
        ('training', 'Formation'),
        ('support', 'Support Technique'),
        ('demo', 'Démonstration'),
    ], string='Service Type', required=True, default='consultation')
    duration = fields.Float(string='Duration (hours)', default=1.0)
    description = fields.Text(string='Description/Notes')
    status = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='Status', default='draft', required=True)
    meeting_link = fields.Char(string='Meeting Link (Zoom/Teams)')
    location = fields.Char(string='Physical Location')
    is_online = fields.Boolean(string='Online Meeting', default=True)
    created_date = fields.Datetime(string='Created', default=lambda self: datetime.now(), readonly=True)
    
    def _get_next_number(self):
        last = self.search([], order='create_date desc', limit=1)
        sequence = 1 if not last else int(last.name.split('-')[-1]) + 1
        return 'RES-%s-%04d' % (datetime.now().strftime('%Y%m%d'), sequence)

    def create(self, vals):
        if 'name' not in vals or not vals['name']:
            vals['name'] = self._get_next_number()
        return super().create(vals)

    def action_confirm(self):
        self.write({'status': 'confirmed'})

    def action_start(self):
        self.write({'status': 'in_progress'})

    def action_complete(self):
        self.write({'status': 'completed'})

    def action_cancel(self):
        self.write({'status': 'cancelled'})
