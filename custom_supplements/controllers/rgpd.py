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

                partner.write({
                    'name': 'Utilisateur supprimé',
                    'email': f'deleted_{partner.id}@deleted.invalid',
                    # 'phone': False,
                    # 'mobile': False,
                    # 'street': False,
                    # 'street2': False,
                    # 'city': False,
                    # 'zip': False,
                    # 'country_id': False,
                })
                user.write({
                    'login': f'deleted_{user.id}@deleted.invalid',
                })

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



