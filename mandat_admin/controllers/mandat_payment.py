# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class MandatPaymentController(http.Controller):

    @http.route('/mandat/save_checkout_data', type='jsonrpc', auth='public', website=True)
    def save_mandat_checkout_data(self, **kwargs):
        order = request.website.sale_get_order()
        if not order:
            return {'success': False, 'error': 'Commande introuvable'}

        order.write({
            'acheteur_siret': kwargs.get('siret', ''),
            'fournisseur_iban': kwargs.get('iban', ''),
            'ordonnateur': kwargs.get('ordonnateur', ''),
            'qualite_ordonnateur': kwargs.get('qualite', ''),
            'comptable_public': kwargs.get('comptable', ''),
            'numero_engagement': kwargs.get('ej', ''),
            'acheteur_service': kwargs.get('service', ''),
            'reference_bon_commande': kwargs.get('reference', ''),
            'payment_mode': 'mandat_administratif',
        })
        return {'success': True}
