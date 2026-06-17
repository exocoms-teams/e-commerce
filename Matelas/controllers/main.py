# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class DormirLux(http.Controller):

    @http.route('/', auth='public', website=True)
    def index(self, **kwargs):
        return request.render('Matelas.home', {})