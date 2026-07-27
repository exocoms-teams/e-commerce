from odoo import models, fields

class TravelPaymentProvider(models.Model):
    _name = 'travel.payment.provider'
    _description = 'Travel Payment Provider'

    name = fields.Char(string='Provider Name', required=True)
    # Default to 10% (was 0.1 which is 0.1%) — adjust to a sensible default
    commission_rate = fields.Float(string='Commission Rate (%)', default=10.0)
    active = fields.Boolean(string='Active', default=True)
    api_url = fields.Char(string='API URL')
    api_key = fields.Char(string='API Key')

    def compute_commission(self, amount):
        # Work per-record and ensure amount is numeric
        self.ensure_one()
        try:
            amt = float(amount) if amount is not None else 0.0
        except Exception:
            amt = 0.0
        return amt * (self.commission_rate / 100)