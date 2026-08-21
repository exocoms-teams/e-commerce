# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ContratMonetique(http.Controller):

    @http.route('/contrat-commercant-cb', type='http', auth='public', website=True, sitemap=True)
    def contrat_monetique(self, **kw):
        return request.render('contrat_monetique_cb.page_contrat_monetique', {})
