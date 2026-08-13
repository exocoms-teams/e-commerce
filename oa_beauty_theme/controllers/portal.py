from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class OABeautyPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        return values

    @http.route(['/my/beauty_profile'], type='http', auth="user", website=True)
    def portal_my_beauty_profile(self, **kw):
        partner = request.env.user.partner_id
        values = {
            'page_name': 'beauty_profile',
            'partner': partner,
        }
        return request.render("oa_beauty_theme.oa_beauty_profile_page", values)

    @http.route(['/my/beauty_profile/submit'], type='http', auth="user", methods=['POST'], website=True)
    def portal_my_beauty_profile_submit(self, **post):
        partner = request.env.user.partner_id
        
        partner.sudo().write({
            'oa_skin_type': post.get('skin_type'),
            'oa_skin_concern': post.get('skin_concern'),
            'oa_fragrance_preference': post.get('fragrance_pref'),
            'oa_newsletter_optin': post.get('newsletter_optin') == 'on',
        })
        
        return request.redirect('/my/beauty_profile?success=1')
