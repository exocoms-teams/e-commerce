# -*- coding: utf-8 -*-
import logging
import traceback

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger('exocoms.filter_menu')


class ExoFilterSidebar(http.Controller):

    # ------------------------------------------------------------------
    # /exo/filter/facets
    # ------------------------------------------------------------------
    @http.route('/exo/filter/facets', type='jsonrpc', auth='public', website=True)
    def facets(self, **kw):
        _logger.info('[EXO-FACETS] === Appel /exo/filter/facets ===')
        try:
            env = request.env

            Cat = env['product.public.category'].sudo()
            all_cats = Cat.search([], order='sequence, name')
            _logger.info('[EXO-FACETS] Catégories trouvées: %d', len(all_cats))

            Prod = env['product.template'].sudo()
            published = Prod.search([('is_published', '=', True)])
            _logger.info('[EXO-FACETS] Produits publiés: %d', len(published))

            active_cat_ids = set(published.mapped('public_categ_ids').ids)
            _logger.info('[EXO-FACETS] Cat IDs actives: %s', active_cat_ids)

            def has_active(cat_id, visited=None):
                if visited is None:
                    visited = set()
                if cat_id in visited:
                    return False
                visited.add(cat_id)
                if cat_id in active_cat_ids:
                    return True
                children = all_cats.filtered(
                    lambda c: c.parent_id.id == cat_id
                )
                return any(has_active(c.id, visited) for c in children)

            def build_tree(cats, parent_id=False, depth=0):
                if depth > 5:
                    return []
                nodes = []
                children = cats.filtered(
                    lambda c: (c.parent_id.id or False) == parent_id
                )
                for cat in children:
                    if not has_active(cat.id):
                        continue
                    sub = build_tree(cats, cat.id, depth + 1)
                    nodes.append({
                        'id':       cat.id,
                        'name':     cat.name,
                        'children': sub,
                    })
                return nodes

            cat_tree = build_tree(all_cats, parent_id=False)
            _logger.info('[EXO-FACETS] Arbre catégories construit: %d noeuds racine', len(cat_tree))

            Attr = env['product.attribute'].sudo()
            attrs = Attr.search([('create_variant', '!=', 'no_variant')])
            attr_list = []
            for a in attrs:
                if a.value_ids:
                    attr_list.append({
                        'id':     a.id,
                        'name':   a.name,
                        'values': [{'id': v.id, 'name': v.name}
                                   for v in a.value_ids],
                    })
            _logger.info('[EXO-FACETS] Attributs: %d', len(attr_list))

            prices = published.mapped('list_price') if published else [0, 1000]
            price_abs_min = int(min(prices)) if prices else 0
            price_abs_max = int(max(prices)) if prices else 1000
            _logger.info('[EXO-FACETS] Prix: min=%s max=%s', price_abs_min, price_abs_max)

            result = {
                'categories':    cat_tree,
                'attributes':    attr_list,
                'price_abs_min': price_abs_min,
                'price_abs_max': price_abs_max,
            }
            _logger.info('[EXO-FACETS] Réponse OK')
            return result

        except Exception as e:
            _logger.error('[EXO-FACETS] ERREUR: %s', str(e))
            _logger.error('[EXO-FACETS] TRACEBACK:\n%s', traceback.format_exc())
            raise

    # ------------------------------------------------------------------
    # /exo/filter/products
    # ------------------------------------------------------------------
    @http.route('/exo/filter/products', type='jsonrpc', auth='public', website=True)
    def products(self, category_ids=None, attrib=None,
                 price_min=None, price_max=None,
                 search=None, order=None, page=0, **kw):

        _logger.info(
            '[EXO-PRODUCTS] === Appel /exo/filter/products === '
            'cat=%s attrib=%s price=%s-%s search=%r order=%s page=%s',
            category_ids, attrib, price_min, price_max, search, order, page
        )
        try:
            Prod = request.env['product.template'].sudo()
            domain = [('is_published', '=', True)]

            if category_ids:
                ids = [int(i) for i in category_ids
                       if str(i).strip().isdigit()]
                if ids:
                    domain += [('public_categ_ids', 'in', ids)]
                _logger.info('[EXO-PRODUCTS] Filtre catégories: %s', ids)

            if attrib:
                for pair in attrib:
                    if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                        _logger.warning('[EXO-PRODUCTS] Attribut invalide ignoré: %s', pair)
                        continue
                    try:
                        domain += [
                            ('attribute_line_ids.value_ids', 'in', [int(pair[1])])
                        ]
                    except (ValueError, TypeError) as e:
                        _logger.warning('[EXO-PRODUCTS] Erreur attribut %s: %s', pair, e)
                        continue

            if price_min is not None:
                try:
                    domain += [('list_price', '>=', float(price_min))]
                except (ValueError, TypeError) as e:
                    _logger.warning('[EXO-PRODUCTS] price_min invalide %s: %s', price_min, e)
            if price_max is not None:
                try:
                    domain += [('list_price', '<=', float(price_max))]
                except (ValueError, TypeError) as e:
                    _logger.warning('[EXO-PRODUCTS] price_max invalide %s: %s', price_max, e)

            search_str = (search or '').strip()
            if search_str:
                domain += [('name', 'ilike', search_str)]

            safe_orders = {
                'name asc', 'name desc',
                'list_price asc', 'list_price desc',
                'create_date desc',
            }
            order_clause = order if order in safe_orders else 'name asc'
            if order and order not in safe_orders:
                _logger.warning('[EXO-PRODUCTS] Ordre non reconnu %r → fallback name asc', order)

            _logger.info('[EXO-PRODUCTS] Domain: %s | order: %s | page: %s', domain, order_clause, page)

            limit  = 12
            offset = int(page) * limit
            total  = Prod.search_count(domain)
            prods  = Prod.search(domain, order=order_clause,
                                 limit=limit, offset=offset)
            _logger.info('[EXO-PRODUCTS] Total: %d | Page: %d | Produits retournés: %d',
                         total, page, len(prods))

            try:
                html_markup = request.env['ir.qweb']._render(
                    'exocoms_filter_menu.products_partial',
                    {'products': prods, 'request': request},
                )
                _logger.info('[EXO-PRODUCTS] Rendu QWeb OK, taille HTML: %d octets', len(str(html_markup)))
            except Exception as qweb_err:
                _logger.error('[EXO-PRODUCTS] ERREUR rendu QWeb: %s\n%s',
                              str(qweb_err), traceback.format_exc())
                raise

            result = {
                'html':  str(html_markup),
                'total': total,
                'page':  int(page),
                'pages': max(1, -(-total // limit)),
            }
            _logger.info('[EXO-PRODUCTS] Réponse OK — total=%d pages=%d', total, result['pages'])
            return result

        except Exception as e:
            _logger.error('[EXO-PRODUCTS] ERREUR CRITIQUE: %s', str(e))
            _logger.error('[EXO-PRODUCTS] TRACEBACK:\n%s', traceback.format_exc())
            raise


class ExoShopController(WebsiteSale):
    """
    Surcharge du controller /shop natif d'Odoo.
    Le template exo_shop_layout (hérite de website_sale.products)
    injecte la sidebar EXOCOMS et remplace la grille par #exo-products.
    """

    @http.route(['/shop', '/shop/page/<int:page>',
                 '/shop/category/<model("product.public.category"):category>',
                 '/shop/category/<model("product.public.category"):category>/page/<int:page>'],
                type='http', auth='public', website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', min_price=0.0,
             max_price=0.0, ppg=False, **post):
        _logger.info('[EXO-SHOP] Chargement page /shop — page=%s category=%s search=%r',
                     page, category, search)
        try:
            response = super().shop(
                page=page, category=category, search=search,
                min_price=min_price, max_price=max_price, ppg=ppg, **post
            )
            _logger.info('[EXO-SHOP] Réponse parent OK — type: %s', type(response).__name__)

            if hasattr(response, 'qcontext'):
                response.qcontext['exo_sidebar_enabled'] = True
                _logger.info('[EXO-SHOP] qcontext mis à jour avec exo_sidebar_enabled=True')
            else:
                _logger.warning('[EXO-SHOP] Réponse sans qcontext — type: %s attrs: %s',
                                type(response).__name__, dir(response))
            return response

        except Exception as e:
            _logger.error('[EXO-SHOP] ERREUR: %s\n%s', str(e), traceback.format_exc())
            raise
