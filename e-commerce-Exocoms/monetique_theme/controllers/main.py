from odoo import http
from odoo.http import request


class Monetique(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        IrModule = request.env['ir.module.module'].sudo()
        sidebar_modules = [
            'exocoms_sidebar_cards',
            'exocoms_sidebar_tree',
            'exocoms_sidebar_accordion',
        ]
        for module_name in sidebar_modules:
            module = IrModule.search([
                ('name', '=', module_name),
                ('state', '=', 'installed'),
            ], limit=1)
            if module:
                return request.redirect('/boutique')

        return request.render('monetique_theme.page_home', {})