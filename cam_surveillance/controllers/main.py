from odoo import http
from odoo.http import request


class CamSurveillance(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        website = request.website
        # Si on est sur le site Cam Surveillance, afficher NOTRE page
        if website and 'Cam Surveillance' in website.name:
            return request.render('cam_surveillance.cam_home', {})
        # Sinon, comportement par défaut de Monétiques
        return request.render('monetique_theme.page_home', {})