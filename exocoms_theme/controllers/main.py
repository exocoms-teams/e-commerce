from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class Exocoms(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        # Ne pas rediriger si :
        # 1. La requête vient d'un iframe (Website Builder)
        # 2. L'utilisateur est connecté en tant qu'admin/éditeur
        # 3. On est en mode édition
        sec_fetch_dest = request.httprequest.headers.get('Sec-Fetch-Dest', '')
        referrer = request.httprequest.referrer or ''
        in_editor = (
            sec_fetch_dest == 'iframe'
            or request.httprequest.args.get('enable_editor')
            or request.httprequest.args.get('with_loader')
            or '/web#' in referrer
            or 'odoo.com/odoo' in referrer
        )
        if in_editor:
            return request.render('exocoms_theme.home', {})

        # Utilisateur interne (admin, éditeur) — afficher sans rediriger
        if not request.env.user._is_public():
            return request.render('exocoms_theme.home', {})

        frontend_lang = request.httprequest.cookies.get('frontend_lang')

        if not frontend_lang:
            # Première visite — français par défaut
            response = request.redirect('/fr/', code=302)
            response.set_cookie(
                'frontend_lang',
                'fr_FR',
                max_age=365 * 24 * 3600,
                path='/'
            )
            return response

        # Respecter le choix de langue du visiteur
        if frontend_lang == 'en_US':
            return request.redirect('/en', code=302)

        return request.redirect('/fr/', code=302)

    @http.route('/services', type='http', auth='public', website=True, sitemap=True)
    def services_page(self, **kw):
        return request.render('exocoms_theme.services_page', {})

    @http.route('/mentions-legales', type='http', auth='public', website=True, sitemap=True)
    def mentions_legales(self, **kw):
        return request.render('exocoms_theme.mentions_legales', {})

    @http.route('/boutique', type='http', auth='public', website=True, sitemap=True)
    def boutique(self, **kw):
        return request.redirect('/shop')