from odoo import http
from odoo.http import request


def _is_module_installed(module_name):
    mod = request.env['ir.module.module'].sudo().search([
        ('name', '=', module_name),
        ('state', '=', 'installed'),
    ], limit=1)
    return bool(mod)


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

        # Stock info — soft dependency on stock module
        stock_installed = _is_module_installed('stock')
        stock_qty = 0
        stock_state = 'hidden'
        if stock_installed and product_variant:
            stock_qty = product_variant.qty_available or 0
            if product.website_availability == 'always':
                stock_state = 'in_stock'
            elif product.website_availability == 'threshold':
                if stock_qty <= 0:
                    stock_state = 'out_of_stock'
                elif stock_qty <= product.stock_threshold:
                    stock_state = 'low_stock'
                else:
                    stock_state = 'in_stock'
            elif product.website_availability == 'never':
                stock_state = 'hidden'

        values = {
            'product': product,
            'related_products': related_products,
            'product_variant': product_variant,
            'ecommerce_images': ecommerce_images,
            'colors': color_ptavs,
            'sizes': size_ptavs,

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

            # Stock
            'stock_qty': stock_qty,
            'stock_state': stock_state,
            'allow_out_of_stock_order': product.allow_out_of_stock_order,
        }

        return request.render(
            'sneakers.page_product',
            values
        )

    @http.route('/cart', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def cart(self, **kwargs):

        order = request.cart
        delivery_installed = _is_module_installed('delivery')

        delivery_methods = []
        if delivery_installed:
            if request.httprequest.method == 'POST':
                carrier_id = kwargs.get('carrier_id')
                if carrier_id and order:
                    carrier = request.env['delivery.carrier'].sudo().browse(int(carrier_id))
                    if carrier.exists():
                        order.sudo().carrier_id = carrier.id

            try:
                delivery_methods = request.env['delivery.carrier'].sudo().search([
                    ('website_published', '=', True),
                    ('company_id', 'in', [request.env.company.id, False]),
                ])
            except Exception:
                delivery_methods = request.env['delivery.carrier'].sudo().search([
                    ('company_id', 'in', [request.env.company.id, False]),
                    ('active', '=', True),
                ])

        values = {
            'order': order,
            'delivery_methods': delivery_methods,
        }

        return request.render(
            'sneakers.page_cart',
            values
        )

    @http.route('/get-product-variant', type='json', auth='public', website=True)
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
