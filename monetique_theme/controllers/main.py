from odoo import http
from odoo.http import request

class Monetique(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        return request.render('monetique_theme.page_home', {})
from . import audit
