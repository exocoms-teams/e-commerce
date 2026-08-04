from odoo import http, fields, _
from odoo.http import request
from odoo.addons.website_sale.controllers import main as website_sale_main


def _is_module_installed(module_name):
    mod = request.env['ir.module.module'].sudo().search([
        ('name', '=', module_name),
        ('state', '=', 'installed'),
    ], limit=1)
    return bool(mod)


def _clear_order_coupons(order):
    """Remove all applied coupons and their reward lines from the order.

    Ensures only one coupon can be active at a time across the shop so
    stacking discounts from different loyalty programs cannot occur.
    """
    if not order or not order.exists():
        return
    reward_lines = order.order_line.filtered(lambda l: l.reward_id)
    if reward_lines:
        reward_lines.unlink()
    if order.applied_coupon_ids:
        order.write({'applied_coupon_ids': [(5, 0, 0)]})
    if order.coupon_point_ids:
        order.write({'coupon_point_ids': [(5, 0, 0)]})
    order._update_programs_and_rewards()


class SneakersWebsiteSale(website_sale_main.WebsiteSale):
    """Inherit Odoo's WebsiteSale controller to enforce single-coupon behaviour.

    Applying a new promo code must replace any previously applied coupon so
    that customers cannot stack discounts from different loyalty programs.
    Also routes default redirects through /shop-sneakers so coupon links
    never bounce via the Odoo default /shop URL.
    """

    def pricelist(self, promo, reward_id=None, **post):
        if not (order_sudo := request.cart):
            return super().pricelist(promo, **post)
        _clear_order_coupons(order_sudo)
        if not post.get('r'):
            post['r'] = '/shop/cart'
        return super().pricelist(promo, reward_id=reward_id, **post)

    def activate_coupon(self, code, r='/shop-sneakers', **kw):
        if not (order_sudo := request.cart):
            return super().activate_coupon(code, r=r, **kw)
        _clear_order_coupons(order_sudo)
        return super().activate_coupon(code, r=r, **kw)

    @http.route('/shop', type='http', auth='public', website=True)
    def shop(self, **kwargs):
        return request.redirect('/shop-sneakers', code=301)


class SneakersController(http.Controller):

    def _get_product_ratings(self, products):

        product_ratings = {}

        for prod in products:

            ratings = request.env['rating.rating'].sudo().search([
                ('res_model', '=', 'product.template'),
                ('res_id', '=', prod.id),
                ('consumed', '=', True),
            ])

            count = len(ratings)

            product_ratings[prod.id] = (
                round(sum(ratings.mapped('rating')) / count)
                if count else 0
            )

        return product_ratings


    @http.route('/', type='http', auth='public', website=True)
    def home(self):

        popular_products = request.env['product.template'].sudo().search(
            [
                ('sale_ok', '=', True),
                ('website_published', '=', True)
            ],
            limit=8
        )


        categories = request.env['product.public.category'].sudo().search(
            [],
            limit=6
        )


        brands = request.env['product.brand'].sudo().search(
            [],
            limit=5
        )

        return request.render(
            'sneakers.page_home',
            {
                'popular_products': popular_products,
                'categories': categories,
                'brands': brands,
            }
        )

    @http.route('/shop', type='http', auth='public', website=True)
    def shop_redirect(self, **kwargs):
        return request.redirect('/shop-sneakers', code=301)

    @http.route('/shop-sneakers', type='http', auth='public', website=True)
    def shop(self, **kwargs):

        # ==========================
        # Catégories principales
        # ==========================

        # Show all categories (all are sneaker-relevant for this store)
        categories = request.env['product.public.category'].sudo().search([
            ('parent_id', '=', False)
        ])

        selected_category = False
        subcategories = request.env['product.public.category'].sudo().search([
            ('parent_id', '!=', False)
        ])

        category_name = kwargs.get('category')
        search = (kwargs.get('search') or '').strip().lower()

        if category_name:

            category = request.env['product.public.category'].sudo().search([
                ('name', '=ilike', category_name)
            ], limit=1)

            if category:

                if category.parent_id:
                    selected_subcategory = category
                else:
                    selected_category = category

                    subcategories = request.env[
                        'product.public.category'
                    ].sudo().search([
                        ('parent_id', '=', selected_category.id)
                    ])

        unique_subcategories = {}

        for cat in subcategories:
            unique_subcategories[cat.name] = cat

        subcategories = list(unique_subcategories.values())
        # ==========================
        # Sous catégorie sélectionnée
        # ==========================

        selected_subcategory = request.env['product.public.category']
        subcategory_id = kwargs.get('subcategory')

        if subcategory_id:
            selected_subcategory = request.env[
                'product.public.category'
            ].sudo().browse(int(subcategory_id))

            if not selected_subcategory.exists():
                selected_subcategory = request.env['product.public.category']


        # ==========================
        # Produits
        # ==========================

        products = request.env['product.template'].sudo().search([
            ('sale_ok', '=', True)
        ])

        # ==========================
        # Recherche
        # ==========================

        if search:

            products = products.filtered(
                lambda p:
                    search in (p.name or "").lower()
                    or search in (p.description_sale or "").lower()
            )

        # Filtre par sous-catégorie
        if selected_subcategory and selected_subcategory.exists():

            if selected_category:
                # Cas 2 : Men/Women/Kids -> filtrer par l'ID exact
                products = products.filtered(
                    lambda p: selected_subcategory.id in p.public_categ_ids.ids
                )
            else:
                # Cas 1 : Shop général -> filtrer par le nom
                products = products.filtered(
                    lambda p: any(
                        cat.name == selected_subcategory.name
                        for cat in p.public_categ_ids
                    )
                )
            
        elif selected_category:

            products = products.filtered(
                lambda p:
                    selected_category.id in p.public_categ_ids.ids
                    or any(
                        cat.parent_id.id == selected_category.id
                        for cat in p.public_categ_ids
                    )
            )

        

        # ==========================
        # Filtre par Brand
        # ==========================

        brand_ids = request.httprequest.args.getlist('brand')

        if brand_ids:

            brand_ids = [
                int(bid)
                for bid in brand_ids
                if bid.isdigit()
            ]

            products = products.filtered(
                lambda p: p.brand_id.id in brand_ids
            )

        # ==========================
        # Filtre par taille
        # ==========================

        size_ids = request.httprequest.args.getlist('size')


        if size_ids:

            products = products.filtered(
                lambda p:
                    any(
                        value.name in size_ids
                        for variant in p.product_variant_ids
                        for value in variant.product_template_attribute_value_ids.product_attribute_value_id
                    )
            )



        # ==========================
        # Filtre par couleur
        # ==========================

        color_ids = request.httprequest.args.getlist('color')


        if color_ids:

            color_ids = [
                int(cid)
                for cid in color_ids
                if cid.isdigit()
            ]


            products = products.filtered(
                lambda p:
                    any(
                        value.id in color_ids
                        for variant in p.product_variant_ids
                        for value in variant.product_template_attribute_value_ids.product_attribute_value_id
                    )
            )



        # ==========================
        # Filtre prix
        # ==========================

        price_min = float(
            request.httprequest.args.get(
                'price_min',
                0
            )
        )


        price_max = float(
            request.httprequest.args.get(
                'price_max',
                9999
            )
        )


        products = products.filtered(
            lambda p:
                price_min <= p.list_price <= price_max
        )



        # ==========================
        # Filtre disponibilité
        # ==========================

        availability = request.httprequest.args.get('availability')

        if availability == "in_stock":

            products = products.filtered(
                lambda p: p.qty_available > 0
            )

        elif availability == "out_of_stock":

            products = products.filtered(
                lambda p: p.qty_available <= 0
            )


        # ==========================
        # Tri produits
        # ==========================

        sort_by = request.httprequest.args.get('sort')


        if sort_by == "price-low":

            products = products.sorted(
                key=lambda p:p.list_price
            )


        elif sort_by == "price-high":

            products = products.sorted(
                key=lambda p:p.list_price,
                reverse=True
            )


        elif sort_by == "newest":

            products = products.sorted(
                key=lambda p:p.create_date,
                reverse=True
            )

        # ==========================
        # Brands
        # ==========================

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

        product_ratings = self._get_product_ratings(products)

        # ==========================
        # Pagination
        # ==========================

        per_page = 12
        page = max(1, int(request.httprequest.args.get('page', 1)))
        total_products = len(products)
        total_pages = max(1, (total_products + per_page - 1) // per_page)
        page = min(page, total_pages)
        offset = (page - 1) * per_page
        products = products[offset:offset + per_page]

        values = {
            'products': products,
            'categories': categories,
            'brands': brands,
            'sizes': sizes,
            'colors': colors,
            'product_ratings': product_ratings,
            'subcategories': subcategories,
            'selected_category': selected_category,
            'search': search,
            'search_category': category_name,
            'current_page': page,
            'total_pages': total_pages,
        }
        return request.render(
            'sneakers.shop_page',
            values
        )
    @http.route('/shop/cart/get_product_quantity',type='jsonrpc',auth='public',website=True)
    def get_product_cart_quantity(self, product_id):

        order = request.cart

        quantity = 0

        if order:

            line = order.order_line.filtered(
                lambda l: l.product_id.id == int(product_id)
            )

            if line:
                quantity = sum(line.mapped('product_uom_qty'))


        return {
            'quantity': quantity
        }
    @http.route('/product/<int:product_id>', type='http', auth='public', website=True)
    def product_page(self, product_id, **kwargs):

        product = request.env['product.template'].sudo().browse(product_id)

        if not product.exists():
            return request.not_found()


        product_variant = product.product_variant_id


        # ==========================
        # Related products
        # ==========================

        related_products = request.env['product.template'].sudo().search([
            ('id', '!=', product.id),
            ('public_categ_ids', 'in', product.public_categ_ids.ids)
        ], limit=4)

        related_product_ratings = self._get_product_ratings(related_products)

        # ==========================
        # Attributes Color / Size
        # ==========================

        color_values = product.attribute_line_ids.filtered(
            lambda line: line.attribute_id.name == "Color"
        ).value_ids


        size_values = product.attribute_line_ids.filtered(
            lambda line: line.attribute_id.name == "Size"
        ).value_ids



        color_ptavs = request.env[
            'product.template.attribute.value'
        ].sudo().search([
            ('product_tmpl_id', '=', product.id),
            ('product_attribute_value_id', 'in', color_values.ids)
        ])


        size_ptavs = request.env[
            'product.template.attribute.value'
        ].sudo().search([
            ('product_tmpl_id', '=', product.id),
            ('product_attribute_value_id', 'in', size_values.ids)
        ])


        material_values = product.attribute_line_ids.filtered(
            lambda line: line.attribute_id.name == "Material"
        ).value_ids


        sole_values = product.attribute_line_ids.filtered(
            lambda line: line.attribute_id.name == "Sole"
        ).value_ids

        # ==========================
        # Ecommerce images
        # ==========================

        ecommerce_images = request.env['product.image'].sudo().search([
            ('product_tmpl_id', '=', product.id)
        ])




        # ==========================
        # Stock
        # ==========================

        stock_qty = 0
        stock_state = 'hidden'


        if product_variant:

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




        # ==========================
        # Sizes display
        # ==========================

        product_sizes = ', '.join(
            product.attribute_line_ids
            .filtered(
                lambda l: l.attribute_id.name == "Size"
            )
            .value_ids
            .mapped('name')
        )

        ratings = request.env['rating.rating'].sudo().search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', product.id),
            ('consumed', '=', True),
        ])

        rating_count = len(ratings)

        average_rating = (
            round(sum(ratings.mapped('rating')) / rating_count)
            if rating_count else 0
        )
        # ==========================
        # Values sent to QWeb
        # ==========================

        values = {

            # Product
            'product': product,
            'product_variant': product_variant,

            # Related
            'related_products': related_products,
            'product_ratings': related_product_ratings,

            # Images
            'ecommerce_images': ecommerce_images,

            # Attributes
            'colors': color_ptavs,
            'sizes': size_ptavs,
            'materials': material_values,
            'soles': sole_values,

            # Description
            'product_description':
                product.description_sale or '',

            # Specifications

            'product_brand':
                product.brand_id.name
                if product.brand_id else '',

            'product_origin':
                product.country_of_origin.name
                    if product.country_of_origin else '',

            # Model = Product name
            'product_model':
                product.name,

            # Odoo native weight
            # valeur en kg
            'product_weight':
                product.weight or 0,

            # Sizes
            'product_sizes':
                product_sizes,

            # Reviews
            # à remplacer par Odoo rating si installé
            'review_count': rating_count,
            'average_rating': average_rating,
            'reviews': ratings,
        
            # Stock
            'stock_qty': stock_qty,

            'stock_state': stock_state,

            'allow_out_of_stock_order':
                product.allow_out_of_stock_order,

            'product_features': [
                "Premium quality",
                "Comfortable design",
                "Durable construction"
            ],

        }



        return request.render(
            'sneakers.page_product',
            values
        )

    @http.route('/cart', type='http', auth='public', website=True)
    def cart_redirect(self, **kwargs):
        return request.redirect('/shop/cart')

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

            if set(selected_ptavs.ids).issubset(set(variant_ptavs.ids)):
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

    @http.route('/confirmation', type='http', auth='public', website=True, sitemap=True)
    def confirmation(self, **kwargs):
        order_id = kwargs.get('order_id')
        order = False
        tx = False
        company = request.env.company

        if order_id:
            order = request.env['sale.order'].sudo().browse(int(order_id))
            if not order.exists():
                order = False

        if order:
            tx = order.transaction_ids[:1] if hasattr(order, 'transaction_ids') else False

        values = {
            'order': order,
            'transaction': tx,
            'is_wire_transfer': tx and tx.provider_id.code == 'wire_transfer' if tx else False,
            'company': company,
        }
        return request.render('sneakers.page_confirmation', values)

    @http.route('/wishlist', type='http', auth='user', website=True)
    def wishlist(self):

        partner = request.env.user.partner_id


        wishes = request.env['product.wishlist'].sudo().search([
            ('partner_id', '=', partner.id)
        ])


        wishlist_products = wishes.mapped('product_id')


        return request.render(
            'sneakers.page_wishlist',
            {
                'wishlist_products': wishlist_products,
                'wishes': wishes,
                'wishlist_page': True,
            }
        )

    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        company = request.website.company_id
        return request.render('sneakers.page_contact', {
            'company_name': company.name,
            'company_address': company.street,
            'company_phone': company.phone,
            'company_email': company.email,
        })

    @http.route('/terms', type='http', auth='public', website=True)
    def terms(self, **kwargs):
        return request.render('sneakers.page_terms', {})

    @http.route('/about', type='http', auth='public', website=True)
    def about(self, **kwargs):
        return request.render('sneakers.page_about', {})

    @http.route('/faq', type='http', auth='public', website=True)
    def faq(self, **kwargs):
        return request.render('sneakers.page_faq', {})

    @http.route('/careers', type='http', auth='public', website=True)
    def careers(self, **kwargs):
        return request.render('sneakers.page_careers', {})

    @http.route('/shipping', type='http', auth='public', website=True)
    def shipping(self, **kwargs):
        return request.render('sneakers.page_shipping', {})

    @http.route('/returns', type='http', auth='public', website=True)
    def returns(self, **kwargs):
        return request.render('sneakers.page_returns', {})

    @http.route('/privacy-policy', type='http', auth='public', website=True)
    def privacy_policy(self, **kwargs):
        return request.render('sneakers.page_privacy_policy', {})

    @http.route('/newsletter/subscribe', type='json', auth='public', csrf=False)
    def newsletter_subscribe(self, **kwargs):
        email = (kwargs.get('email') or '').strip()
        if not email or '@' not in email:
            return {'success': False, 'error': 'Email invalide'}
        existing = request.env['newsletter.subscriber'].sudo().search([
            ('email', '=', email)
        ], limit=1)
        if existing:
            if existing.state == 'subscribed':
                return {'success': False, 'error': 'Déjà inscrit'}
            existing.sudo().write({'state': 'subscribed', 'subscribed_date': fields.Datetime.now})
        else:
            request.env['newsletter.subscriber'].sudo().create({
                'email': email,
                'state': 'subscribed',
            })
        return {'success': True}