# -*- coding: utf-8 -*-
import math
from odoo import http
from odoo.http import request


class ExocomsSidebarController(http.Controller):

    # ------------------------------------------------------------------
    #  Filtrage AJAX + pagination
    # ------------------------------------------------------------------
    @http.route("/exocoms/sidebar/filter",
                type="jsonrpc", auth="public", website=True)
    def sidebar_filter(self, category_ids=None, brand_ids=None,
                       price_min=None, price_max=None, search=None,
                       sort="name asc", ppg=24, page=1, **kw):
        website = request.website
        ppg = max(1, int(ppg))
        page = max(1, int(page))

        Product = request.env["product.template"].sudo()
        domain = self._build_domain(
            website, category_ids or [], brand_ids or [],
            price_min, price_max, search,
        )

        total = Product.search_count(domain)
        page_count = max(1, math.ceil(total / ppg))
        if page > page_count:
            page = page_count
        offset = (page - 1) * ppg

        products = Product.search(
            domain, order=self._safe_sort(sort), limit=ppg, offset=offset,
        )
        html = request.env["ir.qweb"]._render(
            "exocoms_sidebar_cards.products_grid",
            {"products": products, "website": website},
        )
        return {
            "html": html,
            "count": total,
            "page": page,
            "page_count": page_count,
            "ppg": ppg,
        }

    # ------------------------------------------------------------------
    #  Comparaison : tableau comparatif rendu
    # ------------------------------------------------------------------
    @http.route("/exocoms/sidebar/compare",
                type="jsonrpc", auth="public", website=True)
    def sidebar_compare(self, product_ids=None, **kw):
        ids = [int(i) for i in (product_ids or [])][:4]
        products = request.env["product.template"].sudo().browse(ids).exists()

        attr_names = []
        prod_attrs = {}
        for product in products:
            values = {}
            for line in product.attribute_line_ids:
                values[line.attribute_id.name] = ", ".join(
                    line.value_ids.mapped("name")
                )
                if line.attribute_id.name not in attr_names:
                    attr_names.append(line.attribute_id.name)
            prod_attrs[product.id] = values

        html = request.env["ir.qweb"]._render(
            "exocoms_sidebar_cards.compare_table",
            {
                "products": products,
                "attr_names": attr_names,
                "prod_attrs": prod_attrs,
                "website": request.website,
            },
        )
        return {"html": html}

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    def _base_domain(self, website):
        return [
            ("is_published", "=", True),
            ("website_id", "in", [False, website.id]),
        ]

    def _build_domain(self, website, category_ids, brand_ids,
                      price_min, price_max, search):
        domain = self._base_domain(website)
        if category_ids:
            cat_ids = [int(c) for c in category_ids]
            all_cats = request.env["product.public.category"].sudo().search(
                [("id", "child_of", cat_ids)]
            )
            domain.append(("public_categ_ids", "in", all_cats.ids))
        if brand_ids:
            domain.append(("brand_id", "in", [int(b) for b in brand_ids]))
        if price_min not in (None, ""):
            domain.append(("list_price", ">=", float(price_min)))
        if price_max not in (None, ""):
            domain.append(("list_price", "<=", float(price_max)))
        if search:
            domain.append(("name", "ilike", search))
        return domain

    @staticmethod
    def _safe_sort(sort):
        allowed = {
            "name asc": "name asc",
            "name desc": "name desc",
            "price asc": "list_price asc",
            "price desc": "list_price desc",
        }
        return allowed.get(sort, "name asc")
