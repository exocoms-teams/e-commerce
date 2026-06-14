# -*- coding: utf-8 -*-
"""
EXOCOMS — Sidebar Filter AJAX
Contrôleur Odoo 19

Routes :
  GET  /shop                      → surcharge native, injecte exo_categories dans le contexte
  POST /shop/sidebar/filter       → retourne les produits filtrés + HTML de la grille (JSON)
  POST /shop/sidebar/categories   → retourne les compteurs mis à jour après filtrage (JSON)
"""

import json
from odoo import http
from odoo.http import request

try:
    from odoo.addons.website_sale.controllers.main import WebsiteSale
except ImportError:
    from odoo.addons.website_sale.controllers.website_sale import WebsiteSale

PPG = 12   # produits par page


class ExoWebsiteSaleAjax(WebsiteSale):

    # ── /shop : injection du sidebar ─────────────────────────────────────────

    @http.route()
    def shop(self, page=0, category=None, search="", **post):
        response = super().shop(page=page, category=category, search=search, **post)

        cat_ids_param = request.params.get("cat_ids", "")
        active_cat_ids = [int(x) for x in cat_ids_param.split(",") if x.strip().isdigit()]
        search_query   = request.params.get("search", "").strip()
        min_price      = request.params.get("min_price", "")
        max_price      = request.params.get("max_price", "")

        categories = self._exo_build_categories(active_cat_ids)

        if hasattr(response, "qcontext"):
            response.qcontext.update({
                "exo_categories":    categories,
                "exo_active_ids":    active_cat_ids,
                "exo_search":        search_query,
                "exo_min_price":     min_price,
                "exo_max_price":     max_price,
                "exo_ppg":           PPG,
            })
        return response

    # ── /shop/sidebar/filter : retourne grille HTML + meta ───────────────────

    @http.route(
        "/shop/sidebar/filter",
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def sidebar_filter_ajax(self, cat_ids=None, page=0, search="",
                            min_price=None, max_price=None, sort=None, **kw):
        """
        Retourne :
          - products_html   : HTML de la grille produits (cards)
          - product_count   : nombre total de produits correspondants
          - page_count      : nombre de pages
          - current_page    : page courante
          - cat_counts      : dict {cat_id: count} pour mise à jour des badges
          - empty           : bool, True si aucun résultat
        """
        cat_ids   = [int(x) for x in (cat_ids or []) if str(x).isdigit()]
        page      = max(0, int(page or 0))
        search    = (search or "").strip()
        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None

        domain   = self._exo_base_domain()
        domain  += self._exo_cat_domain(cat_ids)
        domain  += self._exo_search_domain(search)
        domain  += self._exo_price_domain(min_price, max_price)

        Product  = request.env["product.template"].sudo()
        order    = self._exo_sort_order(sort)
        total    = Product.search_count(domain)
        products = Product.search(domain, limit=PPG, offset=page * PPG, order=order)

        products_html = request.env["ir.ui.view"]._render_template(
            "exocoms_sidebar_ajax.exo_product_cards",
            {"products": products, "search": search},
        )

        cat_counts = self._exo_cat_counts(cat_ids, search, min_price, max_price)

        return {
            "products_html":  products_html,
            "product_count":  total,
            "page_count":     max(1, -(-total // PPG)),
            "current_page":   page,
            "cat_counts":     cat_counts,
            "empty":          total == 0,
        }

    # ── Domaines ──────────────────────────────────────────────────────────────

    def _exo_base_domain(self):
        w = request.website
        return [
            ("is_published", "=", True),
            ("sale_ok",      "=", True),
            "|",
            ("website_id",   "=", w.id),
            ("website_id",   "=", False),
        ]

    def _exo_cat_domain(self, cat_ids):
        if not cat_ids:
            return []
        # OR entre les catégories sélectionnées (child_of inclut les descendants)
        if len(cat_ids) == 1:
            return [("public_categ_ids", "child_of", cat_ids[0])]
        clauses = []
        for cid in cat_ids:
            clauses += [("public_categ_ids", "child_of", cid), "|"]
        # retire le dernier "|" superflu
        clauses = clauses[:-1]
        # préfixe polonais Odoo : opérateurs avant opérandes
        return ["|"] * (len(cat_ids) - 1) + \
               [("public_categ_ids", "child_of", cid) for cid in cat_ids]

    def _exo_search_domain(self, search):
        if not search:
            return []
        return ["|", "|",
                ("name",            "ilike", search),
                ("description_sale","ilike", search),
                ("categ_id.name",   "ilike", search)]

    def _exo_price_domain(self, min_p, max_p):
        domain = []
        if min_p is not None:
            domain.append(("list_price", ">=", min_p))
        if max_p is not None:
            domain.append(("list_price", "<=", max_p))
        return domain

    def _exo_sort_order(self, sort):
        orders = {
            "price_asc":  "list_price asc",
            "price_desc": "list_price desc",
            "name_asc":   "name asc",
            "newest":     "create_date desc",
        }
        return orders.get(sort, "website_sequence asc, name asc")

    # ── Compteurs par catégorie ───────────────────────────────────────────────

    def _exo_cat_counts(self, active_cat_ids, search="", min_p=None, max_p=None):
        """
        Pour chaque catégorie, calcule combien de produits seraient trouvés
        si on ajoutait CETTE catégorie aux filtres actifs.
        Permet de griser les catégories sans résultat.
        """
        Cat     = request.env["product.public.category"].sudo()
        Product = request.env["product.template"].sudo()
        base    = (self._exo_base_domain()
                   + self._exo_search_domain(search)
                   + self._exo_price_domain(min_p, max_p))

        all_cats = Cat.search([], order="id")
        counts   = {}
        for cat in all_cats:
            d = base + [("public_categ_ids", "child_of", cat.id)]
            counts[cat.id] = Product.search_count(d)
        return counts

    # ── Arbre de catégories ───────────────────────────────────────────────────

    def _exo_build_categories(self, active_cat_ids=None):
        active_cat_ids = active_cat_ids or []
        Cat = request.env["product.public.category"].sudo()
        w   = request.website

        roots = Cat.search(
            [("parent_id", "=", False),
             "|", ("website_id", "=", w.id), ("website_id", "=", False)],
            order="sequence, name",
        )
        return [self._exo_cat_to_dict(c, active_cat_ids) for c in roots]

    def _exo_cat_to_dict(self, cat, active_cat_ids, depth=0):
        Product = request.env["product.template"].sudo()
        w       = request.website
        count   = Product.search_count([
            ("public_categ_ids", "child_of", cat.id),
            ("is_published",     "=",  True),
            ("sale_ok",          "=",  True),
            "|", ("website_id",  "=",  w.id), ("website_id", "=", False),
        ])
        return {
            "id":            cat.id,
            "name":          cat.display_name,
            "icon":          getattr(cat, "x_sidebar_icon", None) or "fa-folder",
            "count":         count,
            "active":        cat.id in active_cat_ids,
            "subcategories": [
                self._exo_cat_to_dict(c, active_cat_ids, depth + 1)
                for c in cat.child_id
            ] if depth < 2 else [],
        }
