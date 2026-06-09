import datetime
from odoo import http
from odoo.http import request


class Monetique(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        return request.render('monetique_theme.page_home', {})

    @http.route('/paiement', type='http', auth='public', website=True)
    def payment_page(self, amount=0, reservation_id=0, **kwargs):
        return request.render('monetique_theme.page_paiement', {
            'error': False,
            'form_data': {'amount': amount, 'reservation_id': reservation_id},
        })

    @http.route('/paiement/traiter', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def process_payment(self, **post):
        try:
            first_name = post.get('first_name', '').strip()
            last_name = post.get('last_name', '').strip()
            email = post.get('email', '').strip()
            phone = post.get('phone', '').strip()
            amount = post.get('amount', '0').strip()
            card_number = post.get('card_number', '').strip()
            card_expiry = post.get('card_expiry', '').strip()
            card_cvv = post.get('card_cvv', '').strip()
            address = post.get('address', '').strip()
            city = post.get('city', '').strip()
            zip_code = post.get('zip_code', '').strip()
            reservation_id = int(post.get('reservation_id', 0))

            if not (first_name and last_name and email and amount and card_number and card_expiry and card_cvv):
                return request.render('monetique_theme.page_paiement', {
                    'error': True,
                    'error_msg': 'Tous les champs obligatoires doivent être remplis',
                    'form_data': post,
                })

            if '@' not in email:
                return request.render('monetique_theme.page_paiement', {
                    'error': True,
                    'error_msg': 'Email invalide',
                    'form_data': post,
                })

            provider = request.env['travel.payment.provider'].sudo().search([], limit=1)

            payment_vals = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'address': address,
                'city': city,
                'zip_code': zip_code,
                'card_last_4': card_number[-4:],
                'currency': 'EUR',
                'state': 'pending',
                'date_transaction': datetime.datetime.now(),
            }

            if reservation_id:
                payment_vals['reservation_id'] = reservation_id
            if provider:
                payment_vals['provider_id'] = provider.id

            payment_record = request.env['travel.payment.transaction'].sudo().create(payment_vals)

            return request.render('monetique_theme.page_paiement_success', {
                'transaction_id': payment_record.id,
                'amount': float(amount),
            })

        except Exception as e:
            return request.render('monetique_theme.page_paiement', {
                'error': True,
                'error_msg': 'Une erreur est survenue lors du traitement du paiement',
                'form_data': post,
            })
