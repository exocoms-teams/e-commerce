from odoo import http
from odoo.http import request
from odoo.addons.monetique_theme.controllers.main import Monetique
from odoo import models, fields
from odoo.addons.website_sale.controllers.main import WebsiteSale


class CamSurveillance(Monetique):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        website = request.website
        if website and 'Cam Surveillance' in website.name:
            return request.render('cam_surveillance.cam_home', {})
        return super().home(**kw)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    view_count = fields.Integer(string="Nombre de clics / vues", default=0, copy=False)

    def track_click(self):
        """Incrémente le compteur de clics de manière sécurisée"""
        for product in self:
            product.sudo().view_count += 1


class WebsiteSaleCustom(WebsiteSale):

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        if product:
            product.track_click()
            
        return super(WebsiteSaleCustom, self).product(product, category=category, search=search, **kwargs)