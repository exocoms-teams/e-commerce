# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class MandatPaymentController(http.Controller):

    @http.route('/mandat/save_checkout_data', type='json', auth='public', website=True)
    def save_mandat_checkout_data(self, **kwargs):
        order = request.website.sale_get_order()
        if not order:
            return {'success': False, 'error': 'Commande introuvable'}

        order.write({
            'mandat_checkout_siret': kwargs.get('siret', ''),
            'mandat_checkout_iban': kwargs.get('iban', ''),
            'mandat_checkout_ordonnateur': kwargs.get('ordonnateur', ''),
            'mandat_checkout_qualite': kwargs.get('qualite', ''),
            'mandat_checkout_comptable': kwargs.get('comptable', ''),
            'mandat_checkout_ej': kwargs.get('ej', ''),
            'mandat_checkout_service': kwargs.get('service', ''),
            'mandat_checkout_reference': kwargs.get('reference', ''),
            'mandat_checkout_filled': True,
            'payment_mode': 'mandat_administratif',
        })
        return {'success': True}
