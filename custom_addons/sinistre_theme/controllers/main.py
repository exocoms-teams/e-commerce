from odoo import http
from odoo.http import request


class SinistreTheme(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        return request.render('sinistre_theme.page_home', {})

    @http.route('/urgence', type='http', auth='public', website=True, sitemap=True)
    def urgence(self, **kw):
        return request.render('sinistre_theme.page_home', {})

    @http.route('/nos-services', type='http', auth='public', website=True, sitemap=True)
    def services(self, **kw):
        return request.render('sinistre_theme.page_home', {})
