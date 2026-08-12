from odoo.addons.portal.controllers.portal import CustomerPortal, get_error
from odoo.http import route, request
from odoo import _
from odoo.exceptions import AccessDenied, UserError
from werkzeug import urls

class CustomPortal(CustomerPortal):

    @route('/my/deactivate_account', type='http', auth='user', website=True, methods=['POST'])
    def deactivate_account(self, validation, password, **post):
        values = self._prepare_portal_layout_values()
        values['get_error'] = get_error
        values['open_deactivate_modal'] = True
        credential = {'login': request.env.user.login, 'password': password, 'type': 'password'}

        if validation != request.env.user.login:
            values['errors'] = {'deactivate': 'validation'}
        else:
            try:
                request.env['res.users']._check_credentials(credential, {'interactive': True})
                
                # Anonymisation avant désactivation
                user = request.env.user.sudo()
                partner = user.partner_id
                partner_id = partner.id
                anon_name = f'Client supprimé #{partner_id}'
                anon_email = f'deleted_{partner_id}@deleted.invalid'

                partner.with_context(mail_notrack=True).write({
                    'name': anon_name,
                    'email': anon_email,
                    'phone': False,
                    'street': False,
                    'street2': False,
                    'city': False,
                    'zip': False,
                    'country_id': False,
                })
                user.with_context(mail_notrack=True).write({
                    'login': anon_email,
                })
                # 3. Commandes — on garde les montants mais on anonymise
                #    les champs nominatifs sur les lignes et notes
                # sales = request.env['sale.order'].search([('partner_id', '=', partner_id)])
                # sales.write({
                #     'note': False,
                # })

                # 4. Factures — on garde le document légal mais on retire
                #    les références nominatives non obligatoires
                # invoices = request.env['account.move'].search([('partner_id', '=', partner_id)])
                # invoices.write({
                #     'narration': False,
                # })

                # 5. Messages/chatter — suppression des messages non contractuels
                request.env['mail.message'].search([
                    ('res_id', '=', partner_id),
                    ('model', '=', 'res.partner'),
                ]).unlink()

                # Désactivation standard
                user._deactivate_portal_user(**post)
                request.session.logout()
                return request.redirect('/web/login?message=%s' % urls.url_quote(_('Account deleted!')))

            except AccessDenied:
                values['errors'] = {'deactivate': 'password'}
            except UserError as e:
                values['errors'] = {'deactivate': {'other': str(e)}}

        return request.render('portal.portal_my_security', values, headers={
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Security-Policy': "frame-ancestors 'self'",
        })



