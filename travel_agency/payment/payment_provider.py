from odoo import models, fields

class TravelPaymentProvider(models.Model):
    _name = 'travel.payment.provider'
    _description = 'Travel Payment Provider'

    name = fields.Char(string='Provider Name', required=True)
    commission_rate = fields.Float(string='Commission Rate (%)', default=0.1)
    active = fields.Boolean(string='Active', default=True)
    api_url = fields.Char(string='API URL')
    api_key = fields.Char(string='API Key')

    def compute_commission(self, amount):
        return amount * (self.commission_rate / 100)