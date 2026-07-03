# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class ExocomsSidebarHomepage(Website):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        return request.redirect('/boutique')