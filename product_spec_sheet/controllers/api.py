# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime

from odoo import http
from odoo.http import request


def _json_response(data, status=200):
    """Réponse JSON normalisée."""
    return request.make_response(
        json.dumps(data, ensure_ascii=False, default=str, indent=2),
        headers=[
            ("Content-Type", "application/json; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Headers", "X-Api-Key, Content-Type"),
            ("Cache-Control", "no-store"),
        ],
        status=status,
    )


def _error(message, status=400, code=None):
    return _json_response({
        "success": False,
        "error":   {"message": message, "code": code or status},
    }, status=status)


class ProductSpecApiController(http.Controller):
    """
    API REST du catalogue produit.

    Authentification : en-tête HTTP `X-Api-Key: psk_xxxxx`
    Base : /api/catalog/v1
    """

    # ── Helper d'authentification ─────────────────────────────────
    def _authenticate(self, endpoint):
        """Valide la clé API. Renvoie (key, error_response|None)."""
        key_value = request.httprequest.headers.get("X-Api-Key")
        if not key_value:
            key_value = request.params.get("api_key")

        remote_ip = request.httprequest.remote_addr
        key, err = request.env["product.spec.api.key"].sudo().authenticate(
            key_value, remote_ip
        )
        if err:
            return None, _error(err, 401)
        return key, None

    def _serialize_product(self, product, key, detail=False):
        """Convertit un produit en dict JSON selon les permissions de la clé."""
        base = request.env["ir.config_parameter"].sudo().get_param("web.base.url", "")

        data = {
            "id":        product.id,
            "reference": product.default_code or "",
            "name":      product.name,
            "category":  product.categ_id.complete_name,
            "url":       f"{base}{product.website_url}" if product.website_url else "",
            "image":     f"{base}/web/image/product.template/{product.id}/image_1920",
            "lifecycle": {
                "state":       product.lifecycle_state,
                "sellable":    product.lifecycle_is_sellable,
                "eol_date":    product.lifecycle_eol_date,
                "replacement": (
                    product.lifecycle_replacement_id.default_code
                    or product.lifecycle_replacement_id.name
                ) if product.lifecycle_replacement_id else None,
            },
        }

        if key.allow_prices:
            price = product.list_price or 0.0
            if key.price_markup:
                price = price * (1 + key.price_markup / 100.0)
            data["price"] = {
                "amount":   round(price, 2),
                "currency": product.currency_id.name,
                "tax_included": False,
            }

        if key.allow_stock:
            data["stock"] = {
                "available": product.qty_available,
                "in_stock":  product.qty_available > 0,
            }

        if detail:
            data["description"] = product.description_sale or ""
            data["logistics"] = {
                "weight_kg": product.weight or None,
                "volume_m3": product.volume or None,
            }
            data["completeness"] = product.spec_completeness

            if key.allow_specs:
                specs = {}
                for categ in product._get_spec_categories():
                    specs[categ.name] = {
                        line.attribute_id.name: line.value
                        for line in product._get_spec_lines_by_category(categ)
                    }
                data["specifications"] = specs

                data["images"] = [
                    f"{base}/web/image/product.image/{img.id}/image_1920"
                    for img in product.product_template_image_ids
                ]

        return data

    def _product_domain(self, key):
        """Domaine de base restreint aux permissions de la clé."""
        domain = [("sale_ok", "=", True), ("website_published", "=", True)]
        if key.categ_ids:
            domain.append(("categ_id", "child_of", key.categ_ids.ids))
        return domain

    # ══════════════════════════════════════════════════════════════
    # GET /api/catalog/v1/products
    # ══════════════════════════════════════════════════════════════
    @http.route("/api/catalog/v1/products", type="http", auth="none",
                methods=["GET", "OPTIONS"], csrf=False, save_session=False)
    def api_products(self, **kw):
        if request.httprequest.method == "OPTIONS":
            return _json_response({})

        t0 = time.time()
        key, err = self._authenticate("products")
        if err:
            return err
        if not key.allow_products:
            return _error("Permission refusée : lecture des produits", 403)

        try:
            limit  = min(int(kw.get("limit", 50)), 200)
            offset = int(kw.get("offset", 0))
        except ValueError:
            return _error("Paramètres limit/offset invalides", 400)

        domain = self._product_domain(key)

        if kw.get("category"):
            domain.append(("categ_id.name", "ilike", kw["category"]))
        if kw.get("search"):
            term = kw["search"]
            domain += ["|", ("name", "ilike", term), ("default_code", "ilike", term)]
        if kw.get("reference"):
            domain.append(("default_code", "=", kw["reference"]))
        if kw.get("updated_since"):
            domain.append(("write_date", ">=", kw["updated_since"]))
        if kw.get("sellable_only") in ("1", "true", "True"):
            domain.append(("lifecycle_is_sellable", "=", True))

        Product = request.env["product.template"].sudo()
        total    = Product.search_count(domain)
        products = Product.search(domain, limit=limit, offset=offset, order="name")

        result = {
            "success": True,
            "pagination": {
                "total":  total,
                "limit":  limit,
                "offset": offset,
                "returned": len(products),
                "has_more": offset + len(products) < total,
            },
            "products": [self._serialize_product(p, key) for p in products],
        }

        key.log_call("products", 200, request.httprequest.remote_addr,
                     int((time.time() - t0) * 1000))
        return _json_response(result)

    # ══════════════════════════════════════════════════════════════
    # GET /api/catalog/v1/products/<id_ou_reference>
    # ══════════════════════════════════════════════════════════════
    @http.route("/api/catalog/v1/products/<string:identifier>", type="http",
                auth="none", methods=["GET", "OPTIONS"], csrf=False, save_session=False)
    def api_product_detail(self, identifier, **kw):
        if request.httprequest.method == "OPTIONS":
            return _json_response({})

        t0 = time.time()
        key, err = self._authenticate("product_detail")
        if err:
            return err
        if not key.allow_products:
            return _error("Permission refusée", 403)

        domain = self._product_domain(key)
        if identifier.isdigit():
            domain.append(("id", "=", int(identifier)))
        else:
            domain.append(("default_code", "=", identifier))

        product = request.env["product.template"].sudo().search(domain, limit=1)
        if not product:
            key.log_call("product_detail", 404, request.httprequest.remote_addr)
            return _error("Produit introuvable", 404)

        key.log_call("product_detail", 200, request.httprequest.remote_addr,
                     int((time.time() - t0) * 1000))
        return _json_response({
            "success": True,
            "product": self._serialize_product(product, key, detail=True),
        })

    # ══════════════════════════════════════════════════════════════
    # GET /api/catalog/v1/categories
    # ══════════════════════════════════════════════════════════════
    @http.route("/api/catalog/v1/categories", type="http", auth="none",
                methods=["GET", "OPTIONS"], csrf=False, save_session=False)
    def api_categories(self, **kw):
        if request.httprequest.method == "OPTIONS":
            return _json_response({})

        key, err = self._authenticate("categories")
        if err:
            return err

        domain = []
        if key.categ_ids:
            domain.append(("id", "child_of", key.categ_ids.ids))

        categories = request.env["product.category"].sudo().search(domain)
        Product = request.env["product.template"].sudo()

        data = []
        for c in categories:
            count = Product.search_count([
                ("categ_id", "=", c.id),
                ("website_published", "=", True),
                ("sale_ok", "=", True),
            ])
            if count:
                data.append({
                    "id":            c.id,
                    "name":          c.name,
                    "full_name":     c.complete_name,
                    "product_count": count,
                })

        key.log_call("categories", 200, request.httprequest.remote_addr)
        return _json_response({"success": True, "categories": data})

    # ══════════════════════════════════════════════════════════════
    # GET /api/catalog/v1/attributes
    # ══════════════════════════════════════════════════════════════
    @http.route("/api/catalog/v1/attributes", type="http", auth="none",
                methods=["GET", "OPTIONS"], csrf=False, save_session=False)
    def api_attributes(self, **kw):
        if request.httprequest.method == "OPTIONS":
            return _json_response({})

        key, err = self._authenticate("attributes")
        if err:
            return err
        if not key.allow_specs:
            return _error("Permission refusée : caractéristiques", 403)

        categories = request.env["product.spec.category"].sudo().search([])
        data = []
        for categ in categories:
            data.append({
                "category":   categ.name,
                "attributes": [
                    {"id": a.id, "name": a.name, "filterable": a.website_filter}
                    for a in categ.attribute_ids
                ],
            })

        key.log_call("attributes", 200, request.httprequest.remote_addr)
        return _json_response({"success": True, "specifications": data})

    # ══════════════════════════════════════════════════════════════
    # POST /api/catalog/v1/shipping/quote
    # ══════════════════════════════════════════════════════════════
    @http.route("/api/catalog/v1/shipping/quote", type="http", auth="none",
                methods=["POST", "OPTIONS"], csrf=False, save_session=False)
    def api_shipping_quote(self, **kw):
        if request.httprequest.method == "OPTIONS":
            return _json_response({})

        t0 = time.time()
        key, err = self._authenticate("shipping_quote")
        if err:
            return err
        if not key.allow_shipping:
            return _error("Permission refusée : calcul de frais de port", 403)

        try:
            payload = json.loads(request.httprequest.data or "{}")
        except ValueError:
            return _error("Corps de requête JSON invalide", 400)

        items = payload.get("items", [])
        if not items:
            return _error("Le champ 'items' est requis : [{reference, quantity}]", 400)

        Product = request.env["product.template"].sudo()
        total_weight = 0.0
        total_volume = 0.0
        unknown = []

        for item in items:
            ref = item.get("reference")
            qty = item.get("quantity", 1)
            product = Product.search([("default_code", "=", ref)], limit=1)
            if not product:
                unknown.append(ref)
                continue
            total_weight += (product.weight or 0.0) * qty
            total_volume += (product.volume or 0.0) * qty

        if total_weight <= 0:
            return _error(
                "Poids introuvable pour les références fournies. "
                "Vérifiez que les fiches produit sont complètes.", 422
            )

        zone_name = payload.get("zone", "France")
        carriers  = request.env["product.spec.carrier"].sudo().search([("active", "=", True)])

        quotes = []
        for carrier in carriers:
            divisor = carrier.volumetric_divisor or 5000
            vol_kg  = (total_volume * 1_000_000) / divisor if total_volume else 0.0
            billed  = max(total_weight, vol_kg)

            if carrier.max_weight_kg and billed > carrier.max_weight_kg:
                continue

            zone = carrier.zone_ids.filtered(lambda z: z.name == zone_name)
            if not zone:
                continue

            price = zone[0].get_price(billed * 1000)
            if price is None:
                continue

            quotes.append({
                "carrier":            carrier.name,
                "zone":               zone_name,
                "billed_weight_kg":   round(billed, 3),
                "volumetric_applied": vol_kg > total_weight,
                "price":              round(price, 2),
                "currency":           request.env.company.currency_id.name,
            })

        quotes.sort(key=lambda q: q["price"])

        key.log_call("shipping_quote", 200, request.httprequest.remote_addr,
                     int((time.time() - t0) * 1000))
        return _json_response({
            "success": True,
            "shipment": {
                "real_weight_kg": round(total_weight, 3),
                "volume_m3":      round(total_volume, 6),
                "zone":           zone_name,
            },
            "unknown_references": unknown,
            "quotes": quotes,
        })

    # ══════════════════════════════════════════════════════════════
    # GET /api/catalog/v1/ping
    # ══════════════════════════════════════════════════════════════
    @http.route("/api/catalog/v1/ping", type="http", auth="none",
                methods=["GET", "OPTIONS"], csrf=False, save_session=False)
    def api_ping(self, **kw):
        if request.httprequest.method == "OPTIONS":
            return _json_response({})

        key, err = self._authenticate("ping")
        if err:
            return err

        return _json_response({
            "success": True,
            "authenticated_as": key.name,
            "partner": key.partner_id.name if key.partner_id else None,
            "permissions": {
                "products": key.allow_products,
                "specs":    key.allow_specs,
                "stock":    key.allow_stock,
                "prices":   key.allow_prices,
                "shipping": key.allow_shipping,
            },
            "rate_limit_hour": key.rate_limit_hour,
            "server_time":     datetime.now().isoformat(),
        })


class MarketplaceFeedController(http.Controller):
    """Flux marketplace accessibles par URL avec jeton."""

    @http.route("/marketplace/feed/<string:token>.<string:ext>", type="http",
                auth="public", csrf=False, sitemap=False)
    def marketplace_feed(self, token, ext, **kw):
        mp = request.env["product.spec.marketplace"].sudo().search([
            ("feed_token", "=", token),
            ("auto_publish", "=", True),
            ("active", "=", True),
        ], limit=1)

        if not mp:
            return request.not_found()

        content, filename, mimetype = mp.generate_feed()

        return request.make_response(content, headers=[
            ("Content-Type", f"{mimetype}; charset=utf-8"),
            ("Content-Disposition", f'inline; filename="{filename}"'),
            ("Cache-Control", "public, max-age=3600"),
        ])
