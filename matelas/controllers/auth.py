# -*- coding: utf-8 -*-
import secrets

from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class MatelasAuthSignupHome(AuthSignupHome):
    """Ajoute une confirmation d'email obligatoire à la création d'un
    compte public (auto-inscription sans jeton d'invitation)."""

    def _signup_with_values(self, token, values, do_login):
        login, password = request.env['res.users'].sudo().signup(values, token)

        if not token:
            # confirmation par email avant que le compte soit utilisable.
            user = request.env['res.users'].sudo().with_context(active_test=False).search(
                [('login', '=', login)], limit=1)
            if user and user.active:
                confirm_token = secrets.token_urlsafe(32)
                user.write({
                    'active': False,
                    'matelas_email_confirm_token': confirm_token,
                })
                self._send_matelas_confirmation_email(user, confirm_token)
                return

        credential = {'login': login, 'password': password, 'type': 'password'}
        if do_login:
            request.session.authenticate(request.env, credential)

    def _send_matelas_confirmation_email(self, user, token):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        confirm_url = '%s/account/confirm/%s' % (base_url, token)

        body_html = '''
        <table width="100%%" cellpadding="0" cellspacing="0" style="max-width:520px;margin:0 auto;font-family:Arial,sans-serif;">
          <tr><td style="text-align:center;padding:32px 24px;">
            <h1 style="color:#0D3B8C;margin-bottom:8px;">MATELAS</h1>
            <p style="color:#3a3a3a;font-size:15px;line-height:1.5;">
              Bonjour %(name)s,<br/><br/>
              Merci de vous être inscrit(e) sur notre site. Pour activer votre
              compte, merci de confirmer votre adresse email en cliquant sur
              le bouton ci-dessous.
            </p>
            <a href="%(confirm_url)s"
               style="display:inline-block;margin-top:16px;padding:12px 28px;
                      background-color:#2E86F5;color:#ffffff;text-decoration:none;
                      border-radius:50px;font-weight:700;">
              Confirmer mon adresse email
            </a>
            <p style="color:#9a9a9a;font-size:12px;margin-top:24px;">
              Si le bouton ne fonctionne pas, copiez ce lien dans votre
              navigateur :<br/>%(confirm_url)s
            </p>
          </td></tr>
        </table>
        ''' % {
            'name': user.name or user.login,
            'confirm_url': confirm_url,
        }

        request.env['mail.mail'].sudo().create({
            'subject': "Confirmez votre adresse email - Matelas",
            'email_from': 'contact@matelas.com',
            'email_to': user.email or user.login,
            'body_html': body_html,
            'auto_delete': True,
        }).send()

    @http.route('/account/confirm/<string:token>', type='http', auth='public', website=True, sitemap=False)
    def matelas_confirm_email(self, token, **kwargs):
        user = request.env['res.users'].sudo().with_context(active_test=False).search(
            [('matelas_email_confirm_token', '=', token)], limit=1)

        if not user:
            return request.render('matelas.email_confirm_invalid', {})

        user.write({
            'active': True,
            'matelas_email_confirm_token': False,
        })
        return request.render('matelas.email_confirm_success', {})
