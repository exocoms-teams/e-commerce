from odoo import http
from odoo.http import request


class SneakersController(http.Controller):


    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kwargs):
        return request.render('sneakers.page_home', {})

    @http.route('/shop-sneakers', type='http', auth='public', website=True)
    def shop(self, **kwargs):

        products = request.env['product.template'].sudo().search([
            ('sale_ok', '=', True)
        ])

        categories = request.env['product.public.category'].sudo().search([])

        brands = request.env['product.brand'].sudo().search([])


        # Récupérer les attributs
        size_attribute = request.env['product.attribute'].sudo().search([
            ('name', '=', 'Size')
        ], limit=1)

        color_attribute = request.env['product.attribute'].sudo().search([
            ('name', '=', 'Color')
        ], limit=1)


        sizes = request.env['product.attribute.value'].sudo().search([
            ('attribute_id', '=', size_attribute.id)
        ]) if size_attribute else []


        colors = request.env['product.attribute.value'].sudo().search([
            ('attribute_id', '=', color_attribute.id)
        ]) if color_attribute else []

        values = {

            'products': products,

            'categories': categories,

            'brands': brands,

            'sizes': sizes,

            'colors': colors,

        }
        return request.render(
            'sneakers.shop_page',
            values
        )
    
    @http.route('/product/<int:product_id>', type='http', auth='public', website=True)
    def product_page(self, product_id, **kwargs):

        product = request.env['product.template'].sudo().browse(product_id)
        product_variant = product.product_variant_id

        related_products = request.env['product.template'].sudo().search([
            ('id', '!=', product.id),
            ('public_categ_ids', 'in', product.public_categ_ids.ids)
        ], limit=4)


        color_values = product.attribute_line_ids.filtered(
            lambda line: line.attribute_id.name == "Color"
        ).value_ids

        size_values = product.attribute_line_ids.filtered(
            lambda line: line.attribute_id.name == "Size"
        ).value_ids

        color_ptavs = request.env['product.template.attribute.value'].sudo().search([
            ('product_tmpl_id', '=', product.id),
            ('product_attribute_value_id', 'in', color_values.ids)
        ])


        size_ptavs = request.env['product.template.attribute.value'].sudo().search([
            ('product_tmpl_id', '=', product.id),
            ('product_attribute_value_id', 'in', size_values.ids)
        ])

        ecommerce_images = request.env['product.image'].sudo().search([
            ('product_tmpl_id', '=', product.id)
        ])


        values = {
            'product': product,
            'related_products': related_products,
            'product_variant': product_variant,
            'ecommerce_images': ecommerce_images,
            'colors': color_ptavs,
            'sizes': size_ptavs,

            # tes autres valeurs
            'review_count': '',
            'reviews': [],
            'product_description': product.description_sale,
            'product_brand': product.brand_id.name if product.brand_id else '',
            
            'product_material': product.material or '',
            'product_sole': product.sole or '',
            'product_weight': product.weight or '',
            'product_origin': product.origin or '',

            'product_sizes': ', '.join(
                product.attribute_line_ids
                .filtered(lambda l: l.attribute_id.name == "Size")
                .value_ids
                .mapped('name')
            ),
        }


        return request.render(
            'sneakers.page_product',
            values
        )

    @http.route('/cart', type='http', auth='public', website=True)
    def cart(self, **kwargs):

        order = request.cart

        values = {
            'order': order,
        }

        return request.render(
            'sneakers.page_cart',
            values
        )

    @http.route('/get-product-variant', type='jsonrpc', auth='public', website=True)
    def get_product_variant(self, template_id, attribute_value_ids):

        template = request.env['product.template'].sudo().browse(
            int(template_id)
        )

        selected_ptavs = request.env[
            'product.template.attribute.value'
        ].sudo().browse(attribute_value_ids)

        for variant in template.product_variant_ids:

            variant_ptavs = variant.product_template_attribute_value_ids

            if set(variant_ptavs.ids) == set(selected_ptavs.ids):
                return {
                    "product_id": variant.id
                }

        return {
            "product_id": False
        }
    @http.route('/checkout', type='http', auth='public', website=True, sitemap=True)
    def checkout(self, **kwargs):
        return request.render('sneakers.page_checkout', {})

    @http.route('/confirmation', type='http', auth='public', website=True, sitemap=True)
    def confirmation(self, **kwargs):
        return request.render('sneakers.page_confirmation', {})

    @http.route('/wishlist', type='http', auth='public', website=True, sitemap=True)
    def wishlist(self, **kwargs):
        return request.render('sneakers.page_wishlist', {})
