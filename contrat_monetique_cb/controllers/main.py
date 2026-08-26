from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class ContratMonetiqueCB(Website):

    @http.route()
    def index(self, **kw):
        return request.render('contrat_monetique_cb.page_contrat_monetique', {})