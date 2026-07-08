from odoo import http
from odoo.http import request


class ExocomsPortalInfogerance(http.Controller):

    def _get_portal_user(self):
        if request.env.user._is_public():
            return False
        return request.env.user

    @http.route('/my/infogerance', type='http', auth='user',
                website=True, sitemap=False)
    def portal_infogerance_dashboard(self, **kw):
        user = self._get_portal_user()
        if not user:
            return request.redirect('/web/login?redirect=/my/infogerance')

        partner = user.partner_id
        contracts = request.env['exocoms.infogerance.contract'].sudo().search([
            ('partner_id', '=', partner.id),
        ], order='create_date desc')

        return request.render(
            'exocoms_infogerance.portal_infogerance_contracts',
            {'contracts': contracts},
        )

    @http.route('/my/infogerance/<int:contract_id>', type='http',
                auth='user', website=True, sitemap=False)
    def portal_infogerance_contract_detail(self, contract_id, **kw):
        user = self._get_portal_user()
        if not user:
            return request.redirect('/web/login')

        contract = request.env['exocoms.infogerance.contract'].sudo().browse(contract_id)
        if not contract.exists() or contract.partner_id != user.partner_id:
            return request.not_found()

        return request.render(
            'exocoms_infogerance.portal_infogerance_contract_detail',
            {'contract': contract},
        )
