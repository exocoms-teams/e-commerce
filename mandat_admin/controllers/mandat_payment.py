# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class MandatPaymentController(http.Controller):

    @http.route('/mandat/save_checkout_data', type='json', auth='public', website=True)
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

    @http.route('/mandat/payment_confirm', type='http', auth='public', methods=['GET', 'POST'], website=True, csrf=False)
    def payment_confirm(self, **kwargs):
        """Confirme la transaction mandat et redirige vers /payment/status."""
        order = request.website.sale_get_order()
        if order:
            tx = order.transaction_ids.filtered(
                lambda t: t.provider_code == 'mandat_administratif' and t.state == 'draft'
            ).sorted('create_date', reverse=True)
            if tx:
                tx[0]._set_pending()
        return request.redirect('/payment/status')
