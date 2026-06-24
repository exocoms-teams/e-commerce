# -*- coding: utf-8 -*-
import pprint
from odoo import http
from odoo.http import request

try:
    from odoo.addons.payment import logging as payment_logging
    _logger = payment_logging.get_payment_logger(__name__)
except Exception:
    import logging
    _logger = logging.getLogger(__name__)


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

    @http.route('/mandat/process', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def process_mandat(self, **post):
        _logger.info("Traitement mandat avec données:\n%s", pprint.pformat(post))
        request.env['payment.transaction'].sudo()._process('mandat_administratif', post)
        return request.redirect('/payment/status')
