from odoo import http
from odoo.http import request


class MonetiquethemeController(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def home(self, **kwargs):
        return request.render('monetique_theme.home')
