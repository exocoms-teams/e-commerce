# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


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

    @http.route('/mandat/submit_payment', type='jsonrpc', auth='public', website=True)
    def submit_payment(self, **kwargs):
        """Sauvegarde les données mandat, crée la transaction et la met en pending."""
        order = request.website.sale_get_order()
        if not order:
            return {'success': False, 'error': 'Commande introuvable'}

        # Sauvegarde des données du mandat
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

        # Trouve le provider mandat_administratif
        provider = request.env['payment.provider'].sudo().search(
            [('code', '=', 'mandat_administratif'), ('state', '!=', 'disabled')], limit=1
        )
        if not provider:
            return {'success': False, 'error': 'Provider introuvable'}

        # Trouve ou crée la transaction
        existing_tx = order.transaction_ids.filtered(
            lambda t: t.provider_code == 'mandat_administratif' and t.state == 'draft'
        ).sorted('create_date', reverse=True)

        if existing_tx:
            tx = existing_tx[0]
        else:
            tx_values = {
                'provider_id': provider.id,
                'amount': order.amount_total,
                'currency_id': order.currency_id.id,
                'partner_id': order.partner_invoice_id.id or order.partner_id.id,
                'operation': 'online_redirect',
            }
            tx = request.env['payment.transaction'].sudo().with_context(
                sale_order_id=order.id
            )._create_payment_transaction(tx_values)

        tx.sudo()._set_pending()
        return {'success': True}

    @http.route('/mandat/payment_confirm', type='http', auth='public', methods=['GET', 'POST'], website=True, csrf=False)
    def payment_confirm(self, **kwargs):
        order = request.website.sale_get_order()
        if order:
            tx = order.transaction_ids.filtered(
                lambda t: t.provider_code == 'mandat_administratif' and t.state == 'draft'
            ).sorted('create_date', reverse=True)
            if tx:
                tx[0]._set_pending()
        return request.redirect('/payment/status')
