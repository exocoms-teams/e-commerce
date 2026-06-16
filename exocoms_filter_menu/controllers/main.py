# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ExoFilterSidebar(http.Controller):

    # ------------------------------------------------------------------
    # /exo/filter/facets
    # Retourne l'arbre catégories 3 niveaux + attributs + bornes prix
    # ------------------------------------------------------------------
    @http.route('/exo/filter/facets', type='json', auth='public', website=True)
    def facets(self, **kw):
        env = request.env

        # Catégories publiques — Odoo 19 : website_published supprimé
        Cat = env['product.public.category'].sudo()
        all_cats = Cat.search([], order='sequence, name')

        # IDs des catégories ayant au moins un produit publié
        Prod = env['product.template'].sudo()
        published = Prod.search([('is_published', '=', True)])
        active_cat_ids = set(published.mapped('public_categ_ids').ids)

        # ERREUR 3 corrigée : has_active avec garde anti-cycles via visited
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
            # Limite de profondeur pour éviter tout débordement
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

        # Attributs produit
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

        # Bornes de prix réelles du catalogue
        prices = published.mapped('list_price') if published else [0, 1000]
        price_abs_min = int(min(prices)) if prices else 0
        price_abs_max = int(max(prices)) if prices else 1000

        return {
            'categories':    cat_tree,
            'attributes':    attr_list,
            'price_abs_min': price_abs_min,
            'price_abs_max': price_abs_max,
        }

    # ------------------------------------------------------------------
    # /exo/filter/products
    # Retourne la grille produits filtrée (HTML) + metadata pagination
    # ------------------------------------------------------------------
    @http.route('/exo/filter/products', type='json', auth='public', website=True)
    def products(self, category_ids=None, attrib=None,
                 price_min=None, price_max=None,
                 search=None, order=None, page=0, **kw):

        Prod = request.env['product.template'].sudo()
        domain = [('is_published', '=', True)]

        # Filtre catégories
        if category_ids:
            ids = [int(i) for i in category_ids
                   if str(i).strip().isdigit()]
            if ids:
                domain += [('public_categ_ids', 'in', ids)]

        # Filtre attributs [[attr_id, value_id], …]
        # ERREUR 2 corrigée : valeurs peuvent arriver en str ou int
        if attrib:
            for pair in attrib:
                if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                    continue
                try:
                    domain += [
                        ('attribute_line_ids.value_ids', 'in', [int(pair[1])])
                    ]
                except (ValueError, TypeError):
                    continue

        # Filtre prix
        if price_min is not None:
            try:
                domain += [('list_price', '>=', float(price_min))]
            except (ValueError, TypeError):
                pass
        if price_max is not None:
            try:
                domain += [('list_price', '<=', float(price_max))]
            except (ValueError, TypeError):
                pass

        # Recherche texte — ERREUR 1 corrigée : search peut être None
        search_str = (search or '').strip()
        if search_str:
            domain += [('name', 'ilike', search_str)]

        # Tri sécurisé — ERREUR 1 bis : order peut être None
        safe_orders = {
            'name asc', 'name desc',
            'list_price asc', 'list_price desc',
            'create_date desc',
        }
        order_clause = order if order in safe_orders else 'name asc'

        # Pagination
        limit  = 12
        offset = int(page) * limit
        total  = Prod.search_count(domain)
        prods  = Prod.search(domain, order=order_clause,
                             limit=limit, offset=offset)

        # Odoo 19 : ir.qweb._render() → convertir Markup en str pour JSON
        html_markup = request.env['ir.qweb']._render(
            'exocoms_filter_menu.products_partial',
            {'products': prods, 'request': request},
        )

        return {
            'html':  str(html_markup),
            'total': total,
            'page':  int(page),
            'pages': max(1, -(-total // limit)),
        }
