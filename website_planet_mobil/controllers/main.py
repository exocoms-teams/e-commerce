from odoo import http
from odoo.http import request

class PlanetMobilController(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        new_products = request.env['product.template'].sudo().search([
            ('is_published', '=', True),
            ('is_new', '=', True),
        ], limit=4)

        best_sellers = request.env['product.template'].sudo().search([
            ('is_published', '=', True),
            ('is_best_seller', '=', True),
        ], limit=4)

        return request.render('website_planet_mobil.homepage', {
            'new_products': new_products,
            'best_sellers': best_sellers,
        })