from odoo import http
from odoo.http import request


class Exocoms(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):

        return request.render('exocoms_theme.home', {})

    @http.route('/services', type='http', auth='public', website=True, sitemap=True)
    def services_page(self, **kw):

        return request.render(
            'exocoms_theme.services_page',
            {}
        )