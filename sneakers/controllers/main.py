from odoo import http
from odoo.http import request


class SneakersController(http.Controller):


    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kwargs):
        return request.render('sneakers.page_home', {})

    @http.route('/shop-sneakers', type='http', auth='public', website=True, sitemap=True)
    def shop(self, **kwargs):
        return request.render('sneakers.shop_page', {})

    
    @http.route('/product/<int:product_id>', type='http', auth='public', website=True, sitemap=True)
    def product(self, product_id, **kwargs):

        product = request.env['product.template'].sudo().browse(product_id)

        if not product.exists():
            return request.not_found()


        similar_products = request.env['product.template'].sudo().search([
            ('public_categ_ids', 'in', product.public_categ_ids.ids),
            ('id', '!=', product.id)
        ], limit=4)

        return request.render('sneakers.page_product', {
            'product': product,
            'similar_products': similar_products,
        })

    @http.route('/cart', type='http', auth='public', website=True)
    def cart(self, **kwargs):

        order = request.cart

        return request.render('sneakers.page_cart', {
            'order': order,
        })

    @http.route('/checkout', type='http', auth='public', website=True, sitemap=True)
    def checkout(self, **kwargs):
        return request.render('sneakers.page_checkout', {})

    @http.route('/confirmation', type='http', auth='public', website=True, sitemap=True)
    def confirmation(self, **kwargs):
        return request.render('sneakers.page_confirmation', {})

    @http.route('/wishlist', type='http', auth='public', website=True, sitemap=True)
    def wishlist(self, **kwargs):
        return request.render('sneakers.page_wishlist', {})
