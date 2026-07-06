# -*- coding: utf-8 -*-
import logging
import pprint
import uuid

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MandatAdministratifController(http.Controller):

    # ── Route standard Odoo payment (patron) ─────────────────────────────
    @http.route('/payment/mandat_administratif/process', type='http', auth='public',
                methods=['POST'], csrf=False)
    def mandat_administratif_process(self, **post):
        _logger.info("Mandat administratif : données reçues :\n%s", pprint.pformat(post))
        request.env['payment.transaction'].sudo()._process('mandat_administratif', post)
        return request.redirect('/payment/status')

    # ── Routes checkout personnalisées ───────────────────────────────────
    def _get_current_order(self):
        order_id = request.session.get('sale_order_id')
        if not order_id:
            return None
        order = request.env['sale.order'].sudo().browse(order_id)
        return order if order.exists() else None

    @http.route('/mandat/submit', type='jsonrpc', auth='public', website=True)
    def submit_mandat(self, **kwargs):
        try:
            return self._submit_mandat_impl(**kwargs)
        except Exception as e:
            _logger.exception('Erreur dans submit_mandat')
            return {'success': False, 'error': str(e)}

    def _submit_mandat_impl(self, **kwargs):
        order = self._get_current_order()
        if not order:
            return {'success': False, 'error': 'Commande introuvable'}

        siret       = kwargs.get('siret', '').strip()
        ordonnateur = kwargs.get('ordonnateur', '').strip()
        comptable   = kwargs.get('comptable', '').strip()

        if not siret or not ordonnateur or not comptable:
            return {'success': False, 'error': 'Champs obligatoires manquants'}

        company      = request.env.company.sudo()
        bank_account = request.env['res.partner.bank'].sudo().search(
            [('partner_id', '=', company.partner_id.id)], limit=1)
        iban = bank_account.acc_number or ''

        write_fields = {'is_mandat_administratif': True}
        mapping = {
            'siret':             'acheteur_siret',
            'ordonnateur':       'ordonnateur',
            'qualite':           'qualite_ordonnateur',
            'comptable':         'comptable_public',
            'ej':                'numero_engagement',
            'service':           'acheteur_service',
            'reference':         'reference_bon_commande',
            'service_chorus':    'service_chorus',
            'code_tiers_chorus': 'code_tiers_chorus',
        }
        for src, dst in mapping.items():
            if hasattr(order, dst):
                write_fields[dst] = kwargs.get(src, '').strip()
        write_fields['fournisseur_iban'] = iban
        order.write(write_fields)

        if order.state in ('draft', 'sent'):
            order.sudo().action_confirm()

        if not order.mandat_numero:
            order.sudo().write({'mandat_numero': order.sudo()._gen_mandat_numero()})

        try:
            with request.env.cr.savepoint():
                provider = request.env['payment.provider'].sudo().search(
                    [('code', '=', 'mandat_administratif'), ('state', '!=', 'disabled')], limit=1)
                if provider:
                    existing_tx = order.transaction_ids.filtered(
                        lambda t: t.provider_code == 'mandat_administratif' and t.state != 'cancel'
                    ).sorted('create_date', reverse=True)
                    if existing_tx:
                        tx = existing_tx[0]
                    else:
                        reference     = f"MANDAT-{order.name}-{uuid.uuid4().hex[:6].upper()}"
                        partner_id    = order.partner_invoice_id.id or order.partner_id.id
                        payment_method = provider.payment_method_ids[:1]
                        tx = request.env['payment.transaction'].sudo().create({
                            'provider_id':       provider.id,
                            'payment_method_id': payment_method.id,
                            'amount':            order.amount_total,
                            'currency_id':       order.currency_id.id,
                            'partner_id':        partner_id,
                            'reference':         reference,
                            'operation':         'online_redirect',
                            'sale_order_ids':    [(4, order.id)],
                        })
                    if tx.state not in ('pending', 'done', 'cancel'):
                        tx.sudo()._set_pending()
                    request.session['__payment_monitored_tx_id__'] = tx.id
        except Exception:
            _logger.exception('Erreur création transaction mandat (non bloquante)')

        request.session['sale_last_order_id'] = order.id
        return {'success': True, 'redirect': '/mandat/confirmation'}

    @http.route('/mandat/confirmation', type='http', auth='public', website=True)
    def mandat_confirmation(self, **kwargs):
        order_id = request.session.get('sale_last_order_id')
        order    = request.env['sale.order'].sudo().browse(order_id) if order_id else None
        if not order or not order.exists():
            return request.redirect('/shop')
        return request.render('mandat_administratif.mandat_confirmation_page', {'order': order})
