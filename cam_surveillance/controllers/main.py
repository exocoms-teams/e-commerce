from odoo import http
from odoo.http import request
from odoo.addons.monetique_theme.controllers.main import Monetique


class CamSurveillance(Monetique):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        website = request.website
        if website and 'Cam Surveillance' in website.name:
            return request.render('cam_surveillance.cam_home', {})
        return super().home(**kw)