from odoo import http
from odoo.http import request


class SneakersController(http.Controller):


    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kwargs):
        return request.render('sneakers.page_home', {})

    @http.route('/shop', type='http', auth='public', website=True, sitemap=True)
    def shop(self, **kwargs):
        return request.render('sneakers.page_shop', {})
    @http.route('/product', type='http', auth='public', website=True, sitemap=True)
    def product(self, **kwargs):
        return request.render('sneakers.page_product', {})

    @http.route('/cart', type='http', auth='public', website=True, sitemap=True)
    def cart(self, **kwargs):
        return request.render('sneakers.page_cart', {})

    @http.route('/checkout', type='http', auth='public', website=True, sitemap=True)
    def checkout(self, **kwargs):
        return request.render('sneakers.page_checkout', {})

    @http.route('/confirmation', type='http', auth='public', website=True, sitemap=True)
    def confirmation(self, **kwargs):
        return request.render('sneakers.page_confirmation', {})
