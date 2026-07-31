from odoo import http, fields
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

        domain = [('sale_ok', '=', True)]

        category_slug = kwargs.get('category', '').strip().lower()
        if category_slug:
            category = request.env['product.public.category'].sudo().search([
                ('name', '=ilike', category_slug)
            ], limit=1)
            if category:
                domain.append(('public_categ_ids', 'in', category.id))

        products = request.env['product.template'].sudo().search(domain)

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
            'active_category': category_slug,
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
                if stock_qty > 0:
                    stock_state = 'in_stock'
                else:
                    stock_state = 'out_of_stock'
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

        # Compute delivery price safely
        delivery_price = 0
        if delivery_installed and order and order.carrier_id:
            try:
                order.sudo()._compute_delivery_price()
                order.sudo()._compute_amounts()
                delivery_price = order.delivery_price
            except Exception:
                delivery_price = order.carrier_id.fixed_price if order.carrier_id else 0

        order_total = order.amount_total if order else 0
        if delivery_price and order_total:
            order_total += delivery_price

        values = {
            'order': order,
            'delivery_methods': delivery_methods,
            'delivery_price': delivery_price,
            'order_total': order_total,
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
                    "product_id": variant.id,
                    "qty_available": variant.qty_available,
                    "available": variant.qty_available > 0
                
                }

        return {
            "product_id": False,
            "qty_available": 0,
            "available": False,
        }

    @http.route('/checkout', type='http', auth='public', website=True, sitemap=True, methods=['GET', 'POST'])
    def checkout(self, **kwargs):
        order = request.cart

        if request.httprequest.method == 'POST' and order:
            # Update partner info
            partner = order.partner_id
            vals = {}
            if kwargs.get('name'):
                vals['name'] = kwargs['name']
            if kwargs.get('email'):
                vals['email'] = kwargs['email']
            if kwargs.get('phone'):
                vals['phone'] = kwargs['phone']
            if kwargs.get('street'):
                vals['street'] = kwargs['street']
            if kwargs.get('city'):
                vals['city'] = kwargs['city']
            if kwargs.get('zip'):
                vals['zip'] = kwargs['zip']
            if kwargs.get('country_id'):
                vals['country_id'] = int(kwargs['country_id'])
            if vals:
                partner.sudo().write(vals)

            # Set delivery method
            if kwargs.get('carrier_id'):
                carrier = request.env['delivery.carrier'].sudo().browse(int(kwargs['carrier_id']))
                if carrier.exists():
                    order.sudo().carrier_id = carrier.id

            # Set payment provider
            payment_provider_id = kwargs.get('payment_provider_id')
            if payment_provider_id:
                order.sudo().payment_provider_id = int(payment_provider_id)

                # Confirm order (wire transfer / manual payment)
                provider = request.env['payment.provider'].sudo().browse(int(payment_provider_id))
                if provider.exists() and provider.code == 'wire_transfer':
                    order.sudo().action_confirm()
                    return request.redirect('/confirmation')

            # If no payment provider selected, still try to confirm
            return request.redirect('/confirmation')

        # Payment providers (only published, website-enabled)
        payment_providers = request.env['payment.provider'].sudo().search([
            ('state', 'in', ['enabled', 'test']),
            ('website_id', 'in', [request.website.id, False]),
        ]) if order else request.env['payment.provider'].sudo().browse()

        # Delivery methods (soft dep on delivery module)
        delivery_installed = _is_module_installed('delivery')
        delivery_methods = []
        if delivery_installed and order:
            try:
                delivery_methods = request.env['delivery.carrier'].sudo().search([
                    ('website_published', '=', True),
                    ('company_id', 'in', [request.env.company.id, False]),
                ])
            except Exception:
                pass

        # Delivery price
        delivery_price = 0
        if delivery_installed and order and order.carrier_id:
            try:
                order.sudo()._compute_delivery_price()
                order.sudo()._compute_amounts()
                delivery_price = order.delivery_price
            except Exception:
                delivery_price = order.carrier_id.fixed_price if order.carrier_id else 0

        # Countries for address form
        countries = request.env['res.country'].sudo().search([])

        # Order lines
        order_lines = order.order_line if order else request.env['sale.order.line'].sudo().browse()

        # Totals
        subtotal = order.amount_untaxed if order else 0
        tax = order.amount_tax if order else 0
        total = order.amount_total if order else 0
        if delivery_price and order:
            total += delivery_price

        # Partner (for pre-filling address)
        partner = order.partner_id if order else request.env.user.partner_id

        values = {
            'order': order,
            'order_lines': order_lines,
            'payment_providers': payment_providers,
            'delivery_methods': delivery_methods,
            'delivery_price': delivery_price,
            'countries': countries,
            'partner': partner,
            'subtotal': subtotal,
            'tax': tax,
            'total': total,
        }
        return request.render('sneakers.page_checkout', values)

    @http.route('/confirmation', type='http', auth='public', website=True, sitemap=True)
    def confirmation(self, **kwargs):
        return request.render('sneakers.page_confirmation', {})

    @http.route('/wishlist', type='http', auth='public', website=True, sitemap=True)
    def wishlist(self, **kwargs):
        return request.render('sneakers.page_wishlist', {})

    @http.route('/contact', type='http', auth='public', website=True, sitemap=True)
    def contact(self, **kwargs):
        company = request.env.company
        company_name = company.name
        company_phone = company.phone or ''
        company_email = company.email or ''
        company_street = company.street or ''
        company_street2 = company.street2 or ''
        company_city = company.city or ''
        company_zip = company.zip or ''
        company_state = company.state_id.name if company.state_id else ''
        company_country = company.country_id.name if company.country_id else ''

        address_parts = [p for p in [company_street, company_street2, company_city, company_zip, company_state, company_country] if p]
        company_address = ', '.join(address_parts) if address_parts else ''

        values = {
            'company_name': company_name,
            'company_phone': company_phone,
            'company_email': company_email,
            'company_address': company_address,
        }
        return request.render('sneakers.page_contact', values)

    @http.route('/terms', type='http', auth='public', website=True, sitemap=True)
    def terms(self, **kwargs):
        return request.render('sneakers.page_terms', {})

    # Newsletter webhooks — N8N integration points

    @http.route('/newsletter/subscribe', type='json', auth='public', website=True)
    def newsletter_subscribe(self, email, name='', **kwargs):
        if not email or '@' not in email:
            return {'status': 'error', 'message': 'Invalid email'}
        existing = request.env['newsletter.subscriber'].sudo().search([
            ('email', '=', email.strip().lower())
        ], limit=1)
        if existing:
            if existing.state == 'subscribed':
                return {'status': 'ok', 'message': 'Already subscribed'}
            existing.sudo().write({'state': 'subscribed', 'subscribed_date': fields.Datetime.now})
            return {'status': 'ok', 'message': 'Re-subscribed'}
        request.env['newsletter.subscriber'].sudo().create({
            'email': email.strip().lower(),
            'name': name,
        })
        return {'status': 'ok', 'message': 'Subscribed'}

    @http.route('/newsletter/unsubscribe', type='json', auth='public', website=True)
    def newsletter_unsubscribe(self, email, **kwargs):
        if not email:
            return {'status': 'error', 'message': 'Email required'}
        subscriber = request.env['newsletter.subscriber'].sudo().search([
            ('email', '=', email.strip().lower())
        ], limit=1)
        if subscriber:
            subscriber.action_unsubscribe()
        return {'status': 'ok', 'message': 'Unsubscribed'}

    @http.route('/newsletter/subscribers', type='json', auth='user', website=True)
    def newsletter_subscribers(self, **kwargs):
        """N8N calls this to get all active subscribers for campaign sending."""
        subscribers = request.env['newsletter.subscriber'].sudo().search([
            ('state', '=', 'subscribed')
        ])
        return {
            'count': len(subscribers),
            'subscribers': [{'email': s.email, 'name': s.name} for s in subscribers],
        }

    # Social media webhook — N8N integration point

    @http.route('/social/publish', type='json', auth='user', website=True)
    def social_publish(self, name, content, platform, image_ids=None, **kwargs):
        """Create a social post record. N8N picks it up and publishes."""
        post = request.env['social.post'].sudo().create({
            'name': name,
            'content': content,
            'platform': platform,
        })
        return {'status': 'ok', 'post_id': post.id}

    # ==========================================
    # CUSTOMER ACCOUNT (SNEEK-33 to SNEEK-36)
    # ==========================================

    @http.route('/my/register', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def register(self, **kwargs):
        if request.httprequest.method == 'POST':
            name = kwargs.get('name', '').strip()
            email = kwargs.get('email', '').strip()
            password = kwargs.get('password', '')

            if not name or not email or not password:
                return request.render('sneakers.page_register', {'error': 'All fields are required.'})

            # Check if email already exists
            existing = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if existing:
                return request.render('sneakers.page_register', {'error': 'An account with this email already exists.'})

            # Create user
            user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'password': password,
                'email': email,
            })

            # Log in
            request.session.authenticate(request.db, email, password)
            return request.redirect('/my/account')

        return request.render('sneakers.page_register', {})

    @http.route('/my/login', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def login(self, redirect='/my/account', **kwargs):
        if request.httprequest.method == 'POST':
            email = kwargs.get('email', '').strip()
            password = kwargs.get('password', '')

            if not email or not password:
                return request.render('sneakers.page_login', {'error': 'Email and password are required.'})

            try:
                request.session.authenticate(request.db, email, password)
                return request.redirect(redirect)
            except Exception:
                return request.render('sneakers.page_login', {'error': 'Invalid email or password.'})

        return request.render('sneakers.page_login', {})

    @http.route('/my/logout', type='http', auth='user', website=True)
    def logout(self, **kwargs):
        request.session.logout()
        return request.redirect('/')

    @http.route('/my/account', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def my_account(self, **kwargs):
        user = request.env.user
        partner = user.partner_id

        if request.httprequest.method == 'POST':
            vals = {}
            if kwargs.get('name'):
                vals['name'] = kwargs['name']
            if kwargs.get('phone'):
                vals['phone'] = kwargs['phone']
            if kwargs.get('street'):
                vals['street'] = kwargs['street']
            if kwargs.get('city'):
                vals['city'] = kwargs['city']
            if kwargs.get('zip'):
                vals['zip'] = kwargs['zip']
            if kwargs.get('country_id'):
                vals['country_id'] = int(kwargs['country_id'])
            if vals:
                partner.sudo().write(vals)

            return request.render('sneakers.page_account', {
                'partner': partner,
                'countries': request.env['res.country'].sudo().search([]),
                'success': 'Profile updated successfully.',
            })

        return request.render('sneakers.page_account', {
            'partner': partner,
            'countries': request.env['res.country'].sudo().search([]),
        })

    @http.route('/my/orders', type='http', auth='user', website=True)
    def my_orders(self, **kwargs):
        orders = request.env['sale.order'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('state', 'in', ['sale', 'done']),
        ], order='date_order desc')

        return request.render('sneakers.page_orders', {
            'orders': orders,
        })