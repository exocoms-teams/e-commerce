from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class WinnersAuthSignup(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        response = super().web_auth_signup(*args, **kw)

        qcontext = self.get_auth_signup_qcontext()
        login = qcontext.get('login')

        if login and not qcontext.get('error'):
            user_sudo = request.env['res.users'].sudo().search(
                request.env['res.users']._get_login_domain(login),
                order=request.env['res.users']._get_login_order(),
                limit=1,
            )
            if user_sudo:
                group_free = request.env.ref('produits_tendance.group_trend_free')
                user_sudo.sudo().write({'groups_id': [(4, group_free.id)]})

        return response