from odoo import http
from odoo.http import request


class SneakersController(http.Controller):


    @http.route('/', type='http', auth='public', website=True)
    def home(self, **kwargs):

        products = request.env['product.template'].sudo().search([
            ('sale_ok', '=', True)
        ], limit=8)


        brands = request.env['product.brand'].sudo().search([])


        values = {
            'products': products,
            'brands': brands,
        }


        return request.render(
            'sneakers.page_home',
            values
        )

    @http.route('/shop-sneakers', type='http', auth='public', website=True, sitemap=True)
    def shop(self, **kwargs):

        Product = request.env['product.template'].sudo()


        products = Product.search([
            ('sale_ok', '=', True)
        ])


        categories = request.env['product.public.category'].sudo().search([])
        brands = request.env['product.brand'].sudo().search([])

        values = {

            'products': products,

            'categories': categories,

            'brands': brands,

            'product_count': len(products),

        }


        return request.render(
            'sneakers.shop_page',
            values
        )

    
    @http.route('/product/<int:product_id>', type='http', auth='public', website=True, sitemap=True)
    def product(self, product_id, **kwargs):

        product = request.env['product.template'].sudo().browse(product_id)

        if not product.exists():
            return request.not_found()


        similar_products = request.env['product.template'].sudo().search([
            ('id', '!=', product.id),
            ('public_categ_ids', 'in', product.public_categ_ids.ids),
            ('sale_ok', '=', True),
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

    @http.route('/wishlist', type='http', auth='public', website=True)
    def wishlist(self):

        wishlist_products = request.env['product.template'].search([], limit=6)

        return request.render(
            'sneakers.page_wishlist',
            {
                'wishlist_products': wishlist_products,
            }
        )
