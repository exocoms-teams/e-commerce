from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class Exocoms(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        # Première visite sans cookie de langue → forcer FR
        frontend_lang = request.httprequest.cookies.get('frontend_lang')
        if not frontend_lang:
            response = request.redirect('/fr/', code=302)
            response.set_cookie('frontend_lang', 'fr_FR', max_age=365 * 24 * 3600)
            return response
        return request.render('exocoms_theme.home', {})

    @http.route('/services', type='http', auth='public', website=True, sitemap=True)
    def services_page(self, **kw):
        return request.render('exocoms_theme.services_page', {})

    @http.route('/mentions-legales', type='http', auth='public', website=True, sitemap=True)
    def mentions_legales(self, **kw):
        return request.render('exocoms_theme.mentions_legales', {})

    @http.route('/boutique', type='http', auth='public', website=True, sitemap=True)
    def boutique(self, **kw):
        return request.redirect('/shop')