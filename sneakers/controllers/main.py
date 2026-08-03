import math
import re
from urllib.parse import urlencode

from markupsafe import Markup, escape

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.tools.translate import LazyTranslate

from odoo.addons.website_sale.const import SHOP_PATH
from odoo.addons.website_sale.controllers.main import WebsiteSale

_lt = LazyTranslate(__name__)

# _lt() (et non request.env._() directement) : ces listes sont évaluées une
# seule fois à l'import du module, hors de toute requête HTTP — un _() classique
# n'aurait aucune langue à résoudre à ce moment-là. _lt() capture le module
# correctement dès maintenant et ne résout la traduction qu'au rendu.
SORT_OPTIONS = [
    ('popular', _lt('Popularity')),
    ('newest', _lt('Newest')),
    ('price-low', _lt('Price : Low to High')),
    ('price-high', _lt('Price : High to Low')),
]


AVAILABILITY_OPTIONS = [
    ('in_stock', _lt('In Stock')),
    ('out_of_stock', _lt('Out of Stock')),
]

# Codes courts utilisés par le <select> du header (sneakers/views/templates/header.xml)
# vers les vrais codes de langue Odoo (res.lang). Volontairement pas de préfixe
# d'URL /fr/, /ar/ pour l'instant — voir EF-023, point de contradiction signalé
# à l'équipe (critère #1 vs section "Hors de portée" du ticket).
LANG_CODE_MAP = {'en': 'en_US', 'fr': 'fr_FR', 'ar': 'ar_001'}


class SneakersController(http.Controller):

    def _shop_url(self, category_id=None, sort_by=None, page=None,
                  brands=None, colors=None, sizes=None, availability=None,
                  price_min=None, price_max=None, search=None):
        query = {}
        if category_id:
            query['category_id'] = category_id
        if sort_by and sort_by != 'popular':
            query['sort_by'] = sort_by
        if page and page != 1:
            query['page'] = page
        if brands:
            query['brand'] = ','.join(brands)
        if colors:
            query['color'] = ','.join(colors)
        if sizes:
            query['size'] = ','.join(sizes)
        if availability:
            query['availability'] = ','.join(availability)
        if price_min is not None:
            query['price_min'] = price_min
        if price_max is not None:
            query['price_max'] = price_max
        if search:
            query['search'] = search
        qs = urlencode(query)
        return '/shop-sneakers' + ('?%s' % qs if qs else '')

    def _toggled(self, current, value):
        return [v for v in current if v != value] if value in current else current + [value]

    FALLBACK_IMAGES = ['product-1.jpg', 'product-2.jpg', 'product-3.jpg', 'product-4.jpg']

    def _product_image_url(self, p):
        """Vraie photo si présente en base, sinon une des 4 images du thème
        (déjà fournies par l'équipe design) au lieu du placeholder gris d'Odoo.
        Répartie par id produit : stable d'un chargement à l'autre, pas aléatoire."""
        if p.image_1024:
            return '/web/image/product.template/%s/image_1024' % p.id
        image = self.FALLBACK_IMAGES[p.id % len(self.FALLBACK_IMAGES)]
        return '/sneakers/static/src/img/products/%s' % image

    def _product_card(self, p, search=None):
        # fields_get() (et non _fields['x'].selection en lecture brute) : passe
        # par la vraie traduction ORM des libellés Selection (ir.model.fields.selection),
        # fiable quel que soit le contexte d'appel (contrairement à env._() dans
        # une compréhension, voir la note plus bas sur ce même souci).
        selections = p.fields_get(['brand', 'color'])
        brand_labels = dict(selections['brand']['selection'])
        color_labels = dict(selections['color']['selection'])
        return {
            'product_id': p.id,
            'product_name': self._highlight(p.name, search) if search else p.name,
            'product_image': self._product_image_url(p),
            'product_price': self._monetary(p.list_price, p.currency_id),
            'product_old_price': '',
            'product_badge': '',
            'product_url': '/product/%s' % p.id,
            'product_brand': brand_labels.get(p.brand, ''),
            'product_color': color_labels.get(p.color, ''),
            'product_size': p.size or '',
            'product_in_stock': p.in_stock,
        }

    def _highlight(self, text, term):
        """Échappe `text` puis entoure les occurrences de `term` de <mark>.
        Retourne un Markup (HTML de confiance) pour un rendu QWeb non ré-échappé."""
        text = text or ''
        if not term:
            return text
        escaped_text = str(escape(text))
        escaped_term = str(escape(term))
        pattern = re.compile(re.escape(escaped_term), re.IGNORECASE)
        return Markup(pattern.sub(lambda m: '<mark>%s</mark>' % m.group(0), escaped_text))

    @http.route('/set_language/<string:lang>', type='http', auth='public', website=True, sitemap=False)
    def set_language(self, lang, r='/', **kwargs):
        """Change la langue de session sans préfixe d'URL (/fr/, /ar/) — voir
        LANG_CODE_MAP. request.redirect() est local=True par défaut, donc `r`
        ne peut pas être utilisé pour une redirection externe (open redirect)."""
        lang_code = LANG_CODE_MAP.get(lang)
        active_lang = request.env['res.lang'].search([('code', '=', lang_code)], limit=1) if lang_code else False
        if not active_lang:
            raise NotFound()
        request.update_context(lang=lang_code)
        # request.future_response (et non redirect.set_cookie) : http_routing's
        # _frontend_pre_dispatch() a déjà programmé un Set-Cookie vers la langue
        # précédente/par défaut sur ce même future_response plus tôt dans ce
        # cycle de requête ; les deux en-têtes seraient sinon concaténés et le
        # navigateur retient le dernier — donc écraser ici, sur le même objet,
        # pour que notre valeur soit celle qui gagne.
        request.future_response.set_cookie('frontend_lang', lang_code)
        return request.redirect(r or '/')

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kwargs):
        return request.render('sneakers.page_home', {})

    @http.route('/shop-sneakers', type='http', auth='public', website=True, sitemap=True)
    def shop(self, category_id=None, sort_by=None, page=1,
             brand=None, color=None, size=None, availability=None,
             price_min=None, price_max=None, search=None, **kwargs):
        search = (search or '').strip()
        Category = request.env['product.public.category']
        Product = request.env['product.template']
        selections = Product.fields_get(['brand', 'color', 'size'])
        brand_labels = dict(selections['brand']['selection'])
        color_labels = dict(selections['color']['selection'])
        size_labels = dict(selections['size']['selection'])

        root_category = Category.search([
            ('name', '=', 'Sneakers'),
            ('parent_id', '=', False),
        ], limit=1)
        categories = root_category.child_id if root_category else Category

        active_category = Category
        if category_id:
            active_category = Category.browse(int(category_id)).exists()

        active_category_id = active_category.id if active_category else None

        active_brands = [v for v in (brand or '').split(',') if v]
        active_colors = [v for v in (color or '').split(',') if v]
        active_sizes = [v for v in (size or '').split(',') if v]
        active_availability = [v for v in (availability or '').split(',') if v]

        try:
            price_min = int(price_min) if price_min not in (None, '') else None
        except ValueError:
            price_min = None
        try:
            price_max = int(price_max) if price_max not in (None, '') else None
        except ValueError:
            price_max = None

        # Bornes min/max réelles du catalogue (indépendantes des filtres actifs,
        # pour que les bornes du slider ne bougent pas quand on filtre).
        catalog_domain = [('is_published', '=', True), ('sale_ok', '=', True)]
        if root_category:
            catalog_domain.append(('public_categ_ids', 'child_of', root_category.id))
        catalog_prices = Product.search(catalog_domain).mapped('list_price')
        catalog_price_min = int(math.floor(min(catalog_prices))) if catalog_prices else 0
        catalog_price_max = int(math.ceil(max(catalog_prices))) if catalog_prices else 0

        active_price_min = price_min if price_min is not None else catalog_price_min
        active_price_max = price_max if price_max is not None else catalog_price_max

        # Position en % des deux poignées sur la piste du slider double, pour dessiner
        # la barre de sélection entre les deux (rendu server-side, pas de JS requis).
        catalog_price_span = catalog_price_max - catalog_price_min
        if catalog_price_span > 0:
            price_min_pct = (active_price_min - catalog_price_min) / catalog_price_span * 100
            price_max_pct = (active_price_max - catalog_price_min) / catalog_price_span * 100
        else:
            price_min_pct = 0
            price_max_pct = 100
        price_min_pct = max(0, min(100, price_min_pct))
        price_max_pct = max(0, min(100, price_max_pct))

        domain = [('is_published', '=', True), ('sale_ok', '=', True)]
        if active_category:
            domain.append(('public_categ_ids', 'child_of', active_category.id))
        elif root_category:
            domain.append(('public_categ_ids', 'child_of', root_category.id))
        if active_brands:
            domain.append(('brand', 'in', active_brands))
        if active_colors:
            domain.append(('color', 'in', active_colors))
        if active_sizes:
            domain.append(('size', 'in', active_sizes))
        if 'in_stock' in active_availability and 'out_of_stock' not in active_availability:
            domain.append(('in_stock', '=', True))
        elif 'out_of_stock' in active_availability and 'in_stock' not in active_availability:
            domain.append(('in_stock', '=', False))
        if price_min is not None:
            domain.append(('list_price', '>=', price_min))
        if price_max is not None:
            domain.append(('list_price', '<=', price_max))
        if search:
            # Recherche full-text : nom, description, SKU (default_code), catégorie.
            domain += ['|', '|', '|',
                       ('name', 'ilike', search),
                       ('description_sale', 'ilike', search),
                       ('default_code', 'ilike', search),
                       ('public_categ_ids.name', 'ilike', search)]

        # "popular" (default) is left as the model's natural order on purpose,
        # real popularity sorting will be implemented later.
        order = {
            'price-low': 'list_price asc',
            'price-high': 'list_price desc',
            'newest': 'create_date desc, id desc',
        }.get(sort_by)

        per_page = 12

        if search:
            # Pertinence simple : correspondance exacte du nom, puis nom qui
            # commence par le terme, puis nom qui le contient, puis le reste
            # (matché uniquement via description/SKU/catégorie).
            search_lower = search.lower()

            def _relevance(product):
                name_lower = (product.name or '').lower()
                if name_lower == search_lower:
                    return 0
                if name_lower.startswith(search_lower):
                    return 1
                if search_lower in name_lower:
                    return 2
                return 3

            all_matches = Product.search(domain).sorted(key=_relevance)
            total_products = len(all_matches)
            total_pages = max(1, (total_products + per_page - 1) // per_page)
            current_page = min(max(1, int(page)), total_pages)
            offset = (current_page - 1) * per_page
            products = all_matches[offset:offset + per_page]
        else:
            total_products = Product.search_count(domain)
            total_pages = max(1, (total_products + per_page - 1) // per_page)
            current_page = min(max(1, int(page)), total_pages)
            products = Product.search(domain, order=order, limit=per_page, offset=(current_page - 1) * per_page)

        product_cards = [self._product_card(p, search=search) for p in products]

        common = dict(sort_by=sort_by, brands=active_brands, colors=active_colors,
                      sizes=active_sizes, availability=active_availability,
                      price_min=price_min, price_max=price_max, search=search)

        category_links = [{
            'id': c.id,
            'name': c.name,
            'url': self._shop_url(category_id=c.id, **common),
            'active': active_category_id == c.id,
        } for c in categories]

        sort_links = [{
            'value': key,
            'label': request.env._(label),
            'url': self._shop_url(category_id=active_category_id, page=1, brands=active_brands,
                                   colors=active_colors, sizes=active_sizes,
                                   availability=active_availability, sort_by=key,
                                   price_min=price_min, price_max=price_max, search=search),
        } for key, label in SORT_OPTIONS]

        brand_links = [{
            'key': key,
            'label': label,
            'active': key in active_brands,
            'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                   brands=self._toggled(active_brands, key),
                                   colors=active_colors, sizes=active_sizes,
                                   availability=active_availability,
                                   price_min=price_min, price_max=price_max, search=search),
        } for key, label in brand_labels.items()]

        color_links = [{
            'key': key,
            'label': label,
            'active': key in active_colors,
            'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                   brands=active_brands, sizes=active_sizes,
                                   colors=self._toggled(active_colors, key),
                                   availability=active_availability,
                                   price_min=price_min, price_max=price_max, search=search),
        } for key, label in color_labels.items()]

        size_links = [{
            'key': key,
            'label': label,
            'active': key in active_sizes,
            'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                   brands=active_brands, colors=active_colors,
                                   sizes=self._toggled(active_sizes, key),
                                   availability=active_availability,
                                   price_min=price_min, price_max=price_max, search=search),
        } for key, label in size_labels.items()]

        availability_links = [{
            'key': key,
            'label': request.env._(label),
            'active': key in active_availability,
            'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                   brands=active_brands, colors=active_colors, sizes=active_sizes,
                                   availability=self._toggled(active_availability, key),
                                   price_min=price_min, price_max=price_max, search=search),
        } for key, label in AVAILABILITY_OPTIONS]

        pages = [{
            'number': n,
            'url': self._shop_url(category_id=active_category_id, page=n, **common),
            'active': n == current_page,
        } for n in range(1, total_pages + 1)]

        availability_labels = {k: request.env._(v) for k, v in AVAILABILITY_OPTIONS}

        active_filter_tags = []

        if active_category:
            active_filter_tags.append({
                'label': active_category.name,
                'url': self._shop_url(sort_by=sort_by, brands=active_brands, colors=active_colors,
                                       sizes=active_sizes, availability=active_availability,
                                       price_min=price_min, price_max=price_max, search=search),
            })

        for key in active_brands:
            active_filter_tags.append({
                'label': brand_labels.get(key, key),
                'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                       brands=self._toggled(active_brands, key), colors=active_colors,
                                       sizes=active_sizes, availability=active_availability,
                                       price_min=price_min, price_max=price_max, search=search),
            })

        for key in active_colors:
            active_filter_tags.append({
                'label': color_labels.get(key, key),
                'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                       brands=active_brands, colors=self._toggled(active_colors, key),
                                       sizes=active_sizes, availability=active_availability,
                                       price_min=price_min, price_max=price_max, search=search),
            })

        for key in active_sizes:
            active_filter_tags.append({
                'label': request.env._(_lt('Size %s', key)),
                'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                       brands=active_brands, colors=active_colors,
                                       sizes=self._toggled(active_sizes, key),
                                       availability=active_availability,
                                       price_min=price_min, price_max=price_max, search=search),
            })

        for key in active_availability:
            active_filter_tags.append({
                'label': availability_labels.get(key, key),
                'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                       brands=active_brands, colors=active_colors, sizes=active_sizes,
                                       availability=self._toggled(active_availability, key),
                                       price_min=price_min, price_max=price_max, search=search),
            })

        if price_min is not None or price_max is not None:
            active_filter_tags.append({
                'label': request.env._(_lt('Price: $%s - $%s', active_price_min, active_price_max)),
                'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                       brands=active_brands, colors=active_colors,
                                       sizes=active_sizes, availability=active_availability,
                                       search=search),
            })

        if search:
            active_filter_tags.append({
                'label': request.env._(_lt('Search: "%s"', search)),
                'url': self._shop_url(category_id=active_category_id, sort_by=sort_by,
                                       brands=active_brands, colors=active_colors,
                                       sizes=active_sizes, availability=active_availability,
                                       price_min=price_min, price_max=price_max),
            })

        has_active_filters = bool(active_filter_tags)

        return request.render('sneakers.shop_page', {
            'all_categories_url': self._shop_url(**common),
            'category_links': category_links,
            'active_category_id': active_category_id,
            'products': product_cards,
            'search': search,
            'total_products': total_products,
            'range_start': (current_page - 1) * per_page + 1 if total_products else 0,
            'range_end': min(current_page * per_page, total_products),
            'sort_by': sort_by or 'popular',
            'sort_links': sort_links,
            'brand_links': brand_links,
            'color_links': color_links,
            'size_links': size_links,
            'availability_links': availability_links,
            'has_active_filters': has_active_filters,
            'active_filter_tags': active_filter_tags,
            'catalog_price_min': catalog_price_min,
            'catalog_price_max': catalog_price_max,
            'active_price_min': active_price_min,
            'active_price_max': active_price_max,
            'price_min_pct': price_min_pct,
            'price_max_pct': price_max_pct,
            'clear_filters_url': self._shop_url(category_id=active_category_id, sort_by=sort_by),
            'total_pages': total_pages,
            'pages': pages,
            'prev_url': self._shop_url(category_id=active_category_id, page=current_page - 1, **common) if current_page > 1 else None,
            'next_url': self._shop_url(category_id=active_category_id, page=current_page + 1, **common) if current_page < total_pages else None,
        })
    @http.route(['/product', '/product/<int:product_id>'], type='http', auth='public', website=True, sitemap=True)
    def product(self, product_id=None, **kwargs):
        Product = request.env['product.template']
        domain = [('is_published', '=', True), ('sale_ok', '=', True)]
        if product_id:
            product = Product.search(domain + [('id', '=', product_id)], limit=1)
            if not product:
                raise NotFound()
        else:
            product = Product.search(domain, order='id asc', limit=1)
            if not product:
                raise NotFound()

        selections = product.fields_get(['brand', 'color'])
        brand_labels = dict(selections['brand']['selection'])
        color_labels = dict(selections['color']['selection'])
        category = product.public_categ_ids[:1]

        related_domain = domain + [('id', '!=', product.id)]
        if category:
            related_domain.append(('public_categ_ids', 'child_of', category.id))
        related_products = Product.search(related_domain, limit=4)

        return request.render('sneakers.page_product', {
            'product': product,
            'product_name': product.name,
            'product_brand': brand_labels.get(product.brand, ''),
            'product_color': color_labels.get(product.color, ''),
            'product_color_key': product.color or '',
            'product_size': product.size or '',
            'product_in_stock': product.in_stock,
            'product_availability_label': request.env._(_lt('In Stock')) if product.in_stock else request.env._(_lt('Out of Stock')),
            'product_category': category.name if category else '',
            'product_image': self._product_image_url(product),
            'product_price_html': self._monetary(product.list_price, product.currency_id),
            'product_description': product.description_sale or '',
            'rating_avg': product.sudo().rating_avg,
            'rating_count': product.sudo().rating_count,
            'related_cards': [self._product_card(p) for p in related_products],
            # Pas de champ réel pour ces données produit (matériau/semelle/poids/
            # origine/caractéristiques/avis) : valeurs vides, à remplir quand ces
            # champs existeront sur le modèle plutôt que d'inventer un contenu.
            'product_features': [],
            'product_model': '',
            'product_material': '',
            'product_sole': '',
            'product_sizes': '',
            'product_weight': '',
            'product_origin': '',
            'reviews': [],
            'review_count': 0,
        })

    def _monetary(self, amount, currency):
        """Comme ir.qweb.field.monetary.value_to_html(), mais avec le symbole
        après le montant en français (119,90 $ plutôt que $ 119,90) — convention
        typographique française. currency.position est un attribut global de la
        devise (pas par langue), donc on ne peut pas juste le changer sans aussi
        affecter l'anglais/l'arabe ; le repositionnement se fait ici uniquement.
        Le séparateur décimal (virgule) reste géré nativement par Odoo (lang.format)."""
        Monetary = request.env['ir.qweb.field.monetary']
        lang = Monetary.user_lang()
        formatted_amount = lang.format('%.{0}f'.format(currency.decimal_places), currency.round(amount), grouping=True) \
            .replace(' ', '\N{NO-BREAK SPACE}').replace('-', '-\N{ZERO WIDTH NO-BREAK SPACE}')
        symbol_after = request.lang.code == 'fr_FR' or currency.position == 'after'
        nbsp = '\N{NO-BREAK SPACE}'
        if symbol_after:
            return Markup('<span class="oe_currency_value">{0}</span>' + nbsp + '{1}').format(
                formatted_amount, currency.symbol or '')
        return Markup('{1}' + nbsp + '<span class="oe_currency_value">{0}</span>').format(
            formatted_amount, currency.symbol or '')

    @http.route('/cart', type='http', auth='public', website=True, sitemap=True)
    def cart(self, **kwargs):
        order = request.cart
        lines = order.order_line if order else request.env['sale.order.line']
        selections = request.env['product.template'].fields_get(['brand', 'color'])
        brand_labels = dict(selections['brand']['selection'])
        color_labels = dict(selections['color']['selection'])

        cart_items = []
        for line in lines:
            p = line.product_id.product_tmpl_id
            category = p.public_categ_ids[:1]
            cart_items.append({
                'line_id': line.id,
                'product_id': p.id,
                'product_url': '/product/%s' % p.id,
                'product_name': p.name,
                'product_image': self._product_image_url(p),
                'product_category': category.name if category else '',
                'product_brand': brand_labels.get(p.brand, ''),
                'product_color': color_labels.get(p.color, ''),
                'product_size': p.size or '',
                'unit_price_html': self._monetary(line.price_unit, order.currency_id),
                'qty': int(line.product_uom_qty),
                'line_total_html': self._monetary(line.price_total, order.currency_id),
            })

        return request.render('sneakers.page_cart', {
            'cart_items': cart_items,
            'cart_subtotal_html': self._monetary(order.amount_untaxed, order.currency_id) if order else self._monetary(0, request.website.currency_id),
            'cart_tax_html': self._monetary(order.amount_tax, order.currency_id) if order else self._monetary(0, request.website.currency_id),
            'cart_total_html': self._monetary(order.amount_total, order.currency_id) if order else self._monetary(0, request.website.currency_id),
            'cart_empty_checkout_label': request.env._(_lt('Empty cart')),
        })

    @http.route('/cart/add/<int:product_id>', type='http', auth='public', website=True, methods=['POST'])
    def cart_add(self, product_id, qty=1, **kwargs):
        product = request.env['product.template'].search([
            ('id', '=', product_id), ('is_published', '=', True), ('sale_ok', '=', True),
        ], limit=1)
        if not product:
            raise NotFound()
        variant = product.product_variant_id
        order = request.cart or request.website._create_cart()
        try:
            qty = max(1, int(qty))
        except ValueError:
            qty = 1
        order._cart_add(product_id=variant.id, quantity=qty)
        return request.redirect('/cart')

    def _cart_line_json(self, order, line):
        return {
            'cart_quantity': order.cart_quantity,
            'line_total_html': self._monetary(line.price_total, order.currency_id) if line else None,
            'subtotal_html': self._monetary(order.amount_untaxed, order.currency_id),
            'tax_html': self._monetary(order.amount_tax, order.currency_id),
            'total_html': self._monetary(order.amount_total, order.currency_id),
        }

    @http.route('/cart/update_line', type='jsonrpc', auth='public', website=True, methods=['POST'])
    def cart_update_line(self, line_id, qty, **kwargs):
        order = request.cart
        if not order:
            return {'error': 'empty_cart'}
        try:
            qty = max(0, int(qty))
        except ValueError:
            return {'error': 'bad_qty'}
        order._cart_update_line_quantity(line_id=int(line_id), quantity=qty)
        line = order.order_line.filtered(lambda l: l.id == int(line_id))
        return self._cart_line_json(order, line)

    @http.route('/cart/remove_line', type='jsonrpc', auth='public', website=True, methods=['POST'])
    def cart_remove_line(self, line_id, **kwargs):
        order = request.cart
        if not order:
            return {'error': 'empty_cart'}
        order._cart_update_line_quantity(line_id=int(line_id), quantity=0)
        return self._cart_line_json(order, None)

    @http.route('/checkout', type='http', auth='public', website=True, sitemap=True)
    def checkout(self, **kwargs):
        return request.render('sneakers.page_checkout', {})

    @http.route('/confirmation', type='http', auth='public', website=True, sitemap=True)
    def confirmation(self, **kwargs):
        return request.render('sneakers.page_confirmation', {})

    @http.route('/wishlist', type='http', auth='public', website=True, sitemap=True)
    def wishlist(self, **kwargs):
        return request.render('sneakers.page_wishlist', {})


class SneakersShopRedirect(WebsiteSale):
    """Retire la page catalogue native (/shop) au profit de /shop-sneakers.

    Ne couvre volontairement que le listing (SHOP_PATH, pagination, catégorie) :
    fiche produit (/shop/<slug>-<id>), panier, checkout et confirmation restent
    sur les routes natives website_sale tant qu'elles ne sont pas reskinnées.
    """

    @http.route(
        [
            SHOP_PATH,
            f'{SHOP_PATH}/page/<int:page>',
            f'{SHOP_PATH}/category/<model("product.public.category"):category>',
            f'{SHOP_PATH}/category/<model("product.public.category"):category>/page/<int:page>',
        ],
        type='http', auth='public', website=True, sitemap=False,
    )
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, tags='', **post):
        query = {}
        if category:
            query['category_id'] = category.id
        if page:
            query['page'] = page
        if search:
            query['search'] = search
        try:
            if float(min_price):
                query['price_min'] = int(float(min_price))
        except ValueError:
            pass
        try:
            if float(max_price):
                query['price_max'] = int(float(max_price))
        except ValueError:
            pass
        url = '/shop-sneakers'
        if query:
            url += '?' + urlencode(query)
        # 302 (temporaire) tant que ce comportement n'est pas validé/committé —
        # à repasser en 301 une fois confirmé définitif, pour éviter tout cache
        # navigateur prématuré pendant qu'on itère encore dessus.
        return request.redirect(url, code=302)
