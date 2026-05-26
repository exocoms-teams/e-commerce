from odoo import http
from odoo.http import request

class SerruproController(http.Controller):

    @http.route('/serrupro', auth='public', website=True, type='http')
    def index(self, **kw):
        return request.render('serrupro.homepage')