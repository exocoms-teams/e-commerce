from odoo import http
from odoo.http import request
 
 
class LegalPagesController(http.Controller):
 
    @http.route('/mentions-legales', type='http', auth='public', website=True, sitemap=True)
    def mentions_legales(self, **kwargs):
        return request.render('produits_tendance.template_mentions_legales', {})
 
    @http.route('/confidentialite', type='http', auth='public', website=True, sitemap=True)
    def confidentialite(self, **kwargs):
        return request.render('produits_tendance.template_confidentialite', {})
 
    @http.route('/cgu', type='http', auth='public', website=True, sitemap=True)
    def cgu(self, **kwargs):
        return request.render('produits_tendance.template_cgu', {})