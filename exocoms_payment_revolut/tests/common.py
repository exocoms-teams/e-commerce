# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

from odoo.addons.payment.tests.common import PaymentCommon


class RevolutCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.revolut = cls._prepare_provider('revolut', update_values={
            'revolut_secret_key': 'sk_dummy_secret_key',
            'revolut_webhook_secret': 'wsk_dummy_signing_secret',
        })
        cls.provider = cls.revolut
        cls.currency = cls.currency_euro

        cls.order_id = '9fc01989-3f61-4484-a5d9-ffe768531be9'
        cls.checkout_url = f'https://checkout.revolut.com/payment-link/{cls.order_id}'

    def _build_order_data(self, state='completed', **kwargs):
        """Return a minimal Revolut order payload matching the test transaction."""
        data = {
            'id': self.order_id,
            'state': state,
            'amount': 111111,  # `PaymentCommon.amount` is 1111.11 EUR, in minor units.
            'currency': 'EUR',
            'checkout_url': self.checkout_url,
            'merchant_order_data': {'reference': self.reference},
            'metadata': {'odoo_reference': self.reference},
            'payments': [{'payment_method': {'type': 'card'}}],
        }
        data.update(kwargs)
        return data
