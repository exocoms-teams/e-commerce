# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

# Version d'API Merchant ciblee (en-tete `Revolut-Api-Version`).
API_VERSION = '2026-08-17'

# URL de base de la Merchant API, selon l'etat du fournisseur.
API_BASE_URLS = {
    'enabled': 'https://merchant.revolut.com/api/',
    'test': 'https://sandbox-merchant.revolut.com/api/',
    'disabled': 'https://sandbox-merchant.revolut.com/api/',
}

# Devises acceptees par Revolut Merchant (ISO 4217).
SUPPORTED_CURRENCIES = [
    'AED', 'AUD', 'BGN', 'CAD', 'CHF', 'CZK', 'DKK', 'EUR', 'GBP', 'HKD',
    'HUF', 'ILS', 'ISK', 'JPY', 'MXN', 'NOK', 'NZD', 'PLN', 'QAR', 'RON',
    'SAR', 'SEK', 'SGD', 'THB', 'TRY', 'USD', 'ZAR',
]

# Devises dont l'unite mineure n'est pas 1/100 sont gerees par
# `payment.const.CURRENCY_MINOR_UNITS`; rien a redefinir ici.

# Moyens de paiement actives automatiquement a l'activation du fournisseur.
DEFAULT_PAYMENT_METHOD_CODES = {
    # Moyens de paiement principaux.
    'card',
    'revolut_pay',
    # Marques.
    'visa',
    'mastercard',
    'amex',
    'maestro',
}

# Correspondance code Odoo -> code Revolut (`payment_method.type`).
PAYMENT_METHODS_MAPPING = {
    'card': 'card',
    'revolut_pay': 'revolut_pay',
    'sepa_direct_debit': 'sepa_direct_debit',
    'open_banking': 'pay_by_bank',
}

# Types Revolut normalises avant recherche du moyen de paiement Odoo.
PAYMENT_METHOD_TYPE_NORMALIZATION = {
    'revolut_pay_card': 'revolut_pay',
    'revolut_pay_account': 'revolut_pay',
    'apple_pay': 'card',
    'google_pay': 'card',
}

# Correspondance etat de commande Revolut -> etat de transaction Odoo.
PAYMENT_STATUS_MAPPING = {
    'pending': ('pending', 'processing'),
    'authorized': ('authorised',),
    'done': ('completed',),
    'cancel': ('cancelled',),
    'error': ('failed', 'declined'),
}

# Evenements webhook souscrits lors de l'enregistrement automatique.
WEBHOOK_EVENTS = [
    'ORDER_AUTHORISED',
    'ORDER_COMPLETED',
    'ORDER_CANCELLED',
    'ORDER_PAYMENT_AUTHENTICATED',
    'ORDER_PAYMENT_DECLINED',
    'ORDER_PAYMENT_FAILED',
]

# Tolerance de rejeu sur l'en-tete `Revolut-Request-Timestamp` (millisecondes).
WEBHOOK_TIMESTAMP_TOLERANCE_MS = 5 * 60 * 1000
