from odoo import http
from odoo.http import request


class ExocomsInfogerance(http.Controller):

    @http.route('/infogerance/detail', type='http', auth='public',
                website=True, sitemap=True)
    def infogerance_detail(self, **kw):
        return request.render(
            'exocoms_infogerance.infogerance_detail_page', {})

    @http.route('/infogerance/request-quote', type='http', auth='public',
                website=True, methods=['POST'])
    def request_quote(self, **post):
        partner = request.env.user.partner_id
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=/infogerance')

        values = {
            'partner_id': partner.id,
            'name': 'Demande infogérance - %s' % partner.name,
        }
        contract = request.env['exocoms.infogerance.contract'].sudo().create(values)
        return request.redirect('/my/infogerance/%s' % contract.id)
