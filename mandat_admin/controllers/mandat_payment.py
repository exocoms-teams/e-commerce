# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MandatPaymentController(http.Controller):

    @http.route('/mandat/submit', type='http', auth='public', methods=['POST'],
                website=True, csrf=False)
    def submit_mandat(self, **post):
        """Reçoit le formulaire mandat, crée la transaction et redirige vers /payment/status."""
        order = request.website.sale_get_order()
        if not order:
            return request.redirect('/shop')

        siret = post.get('siret', '').strip()
        iban = post.get('iban', '').strip()
        ordonnateur = post.get('ordonnateur', '').strip()
        comptable = post.get('comptable', '').strip()

        if not siret or not iban or not ordonnateur or not comptable:
            return request.redirect('/shop/payment?mandat_error=1')

        # Sauvegarde des données mandat sur la commande
        fields = {
            'payment_mode': 'mandat_administratif',
        }
        if hasattr(order, 'acheteur_siret'):
            fields.update({
                'acheteur_siret': siret,
                'fournisseur_iban': iban,
                'ordonnateur': ordonnateur,
                'qualite_ordonnateur': post.get('qualite', ''),
                'comptable_public': comptable,
                'numero_engagement': post.get('ej', ''),
                'acheteur_service': post.get('service', ''),
                'reference_bon_commande': post.get('reference', ''),
            })
        order.write(fields)

        # Trouve le provider
        provider = request.env['payment.provider'].sudo().search(
            [('code', '=', 'mandat_administratif'), ('state', '!=', 'disabled')], limit=1
        )
        if not provider:
            _logger.error('Provider mandat_administratif introuvable')
            return request.redirect('/shop/payment')

        # Réutilise une transaction draft existante ou en crée une
        existing_tx = order.transaction_ids.filtered(
            lambda t: t.provider_code == 'mandat_administratif' and t.state == 'draft'
        ).sorted('create_date', reverse=True)

        if existing_tx:
            tx = existing_tx[0]
        else:
            tx = request.env['payment.transaction'].sudo().with_context(
                sale_order_id=order.id
            )._create_payment_transaction({
                'provider_id': provider.id,
                'amount': order.amount_total,
                'currency_id': order.currency_id.id,
                'partner_id': order.partner_invoice_id.id or order.partner_id.id,
                'operation': 'online_redirect',
            })

        tx.sudo()._set_pending()
        _logger.info('Mandat transaction %s set to pending', tx.reference)
        return request.redirect('/payment/status')

    @http.route('/mandat/save_checkout_data', type='jsonrpc', auth='public', website=True)
    def save_mandat_checkout_data(self, **kwargs):
        order = request.website.sale_get_order()
        if not order:
            return {'success': False, 'error': 'Commande introuvable'}
        fields = {'payment_mode': 'mandat_administratif'}
        if hasattr(order, 'acheteur_siret'):
            fields.update({
                'acheteur_siret': kwargs.get('siret', ''),
                'fournisseur_iban': kwargs.get('iban', ''),
                'ordonnateur': kwargs.get('ordonnateur', ''),
                'qualite_ordonnateur': kwargs.get('qualite', ''),
                'comptable_public': kwargs.get('comptable', ''),
                'numero_engagement': kwargs.get('ej', ''),
                'acheteur_service': kwargs.get('service', ''),
                'reference_bon_commande': kwargs.get('reference', ''),
            })
        order.write(fields)
        return {'success': True}
