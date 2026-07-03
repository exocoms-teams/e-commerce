# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.user.controllers.main import MonetiqueWebsite


class ExocomsSidebarHomepage(MonetiqueWebsite):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        return request.redirect('/boutique')