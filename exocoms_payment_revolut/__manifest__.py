# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.
{
    "name": "Paiement : Revolut Business",
    "version": "20.0.1.0.0",
    "category": "Accounting/Payment Providers",
    "sequence": 350,
    "summary": "Encaissement en ligne via la Merchant API de Revolut Business.",
    "description": " ",
    "author": "EXOCOMS Group",
    "website": "https://www.exocoms.fr",
    "license": "OPL-1",
    "depends": ["payment"],
    "data": [
        "views/payment_provider_views.xml",
        "data/payment_provider_data.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
