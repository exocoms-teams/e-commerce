# -*- coding: utf-8 -*-
import logging
import uuid
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MandatPaymentController(http.Controller):

    def _get_current_order(self):
        """Récupère la commande courante depuis la session."""
        order_id = request.session.get('sale_order_id')
        if not order_id:
            return None
        order = request.env['sale.order'].sudo().browse(order_id)
        return order if order.exists() else None

    @http.route('/mandat/submit', type='jsonrpc', auth='public', website=True)
    def submit_mandat(self, **kwargs):
        """Valide, confirme la commande et crée la transaction mandat."""
        try:
            return self._submit_mandat_impl(**kwargs)
        except Exception as e:
            _logger.exception('Erreur dans submit_mandat')
            return {'success': False, 'error': str(e)}

    def _submit_mandat_impl(self, **kwargs):
        order = self._get_current_order()
        if not order:
            return {'success': False, 'error': 'Commande introuvable'}

        siret = kwargs.get('siret', '').strip()
        iban = kwargs.get('iban', '').strip()
        ordonnateur = kwargs.get('ordonnateur', '').strip()
        comptable = kwargs.get('comptable', '').strip()

        if not siret or not iban or not ordonnateur or not comptable:
            return {'success': False, 'error': 'Champs obligatoires manquants'}

        # 1. Sauvegarde des données mandat sur la commande
        write_fields = {'payment_mode': 'mandat_administratif'}
        mapping = {
            'siret': 'acheteur_siret', 'iban': 'fournisseur_iban',
            'ordonnateur': 'ordonnateur', 'qualite': 'qualite_ordonnateur',
            'comptable': 'comptable_public', 'ej': 'numero_engagement',
            'service': 'acheteur_service', 'reference': 'reference_bon_commande',
        }
        for src, dst in mapping.items():
            if hasattr(order, dst):
                write_fields[dst] = kwargs.get(src, '').strip()
        order.write(write_fields)

        # 2. Confirmation de la commande
        if order.state in ('draft', 'sent'):
            order.sudo().action_confirm()
        _logger.info('Commande %s confirmée via mandat administratif', order.name)

        # 3. Création de la transaction (pour suivi backend)
        try:
            provider = request.env['payment.provider'].sudo().search(
                [('code', '=', 'mandat_administratif'), ('state', '!=', 'disabled')], limit=1
            )
            if provider:
                existing_tx = order.transaction_ids.filtered(
                    lambda t: t.provider_code == 'mandat_administratif' and t.state != 'cancel'
                ).sorted('create_date', reverse=True)

                if existing_tx:
                    tx = existing_tx[0]
                else:
                    reference = f"MANDAT-{order.name}-{uuid.uuid4().hex[:6].upper()}"
                    partner_id = order.partner_invoice_id.id or order.partner_id.id
                    tx = request.env['payment.transaction'].sudo().create({
                        'provider_id': provider.id,
                        'amount': order.amount_total,
                        'currency_id': order.currency_id.id,
                        'partner_id': partner_id,
                        'reference': reference,
                        'operation': 'online_redirect',
                        'sale_order_ids': [(4, order.id)],
                    })
                if tx.state not in ('pending', 'done', 'cancel'):
                    tx.sudo()._set_pending()
                request.session['__payment_monitored_tx_id__'] = tx.id
                _logger.info('Transaction mandat %s mise en pending', tx.reference)
        except Exception:
            _logger.exception('Erreur création transaction mandat (non bloquante)')

        # 4. Prépare la session pour la page de confirmation
        request.session['sale_last_order_id'] = order.id

        return {'success': True, 'redirect': '/shop/confirmation'}

    @http.route('/mandat/save_checkout_data', type='jsonrpc', auth='public', website=True)
    def save_mandat_checkout_data(self, **kwargs):
        order = self._get_current_order()
        if not order:
            return {'success': False, 'error': 'Commande introuvable'}
        write_fields = {'payment_mode': 'mandat_administratif'}
        mapping = {
            'siret': 'acheteur_siret', 'iban': 'fournisseur_iban',
            'ordonnateur': 'ordonnateur', 'qualite': 'qualite_ordonnateur',
            'comptable': 'comptable_public', 'ej': 'numero_engagement',
            'service': 'acheteur_service', 'reference': 'reference_bon_commande',
        }
        for src, dst in mapping.items():
            if hasattr(order, dst):
                write_fields[dst] = kwargs.get(src, '')
        order.write(write_fields)
        return {'success': True}
