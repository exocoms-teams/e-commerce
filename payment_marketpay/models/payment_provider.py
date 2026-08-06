# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('marketpay', "Marketpay")], ondelete={'marketpay': 'set default'}
    )
    marketpay_merchant_id = fields.Char(
        string="Marketpay Merchant ID",
        help="The ID solely used to identify the account with Marketpay",
        required_if_provider='marketpay'
    )
    marketpay_secret_key = fields.Char(
        string="Marketpay Secret Key",
        help="The secret key used to verify the signature of webhook and redirect requests",
        required_if_provider='marketpay'
    )
    marketpay_key_id = fields.Char(
        string="Marketpay Key ID",
        required_if_provider='marketpay'
    )

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'marketpay':
            return default_codes
        return const_get_default_marketpay()

def const_get_default_marketpay():
    return {'card'}
