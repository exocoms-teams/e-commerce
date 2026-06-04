import math

from odoo import _, http
from odoo.http import request


class AutoWebsiteController(http.Controller):
    def _parse_int(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _parse_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _normalize_range(self, min_value, max_value):
        if min_value is not None and max_value is not None and min_value > max_value:
            return max_value, min_value
        return min_value, max_value

    def _get_public_vehicle(self, vehicle_id):
        vehicle = request.env["auto.vehicle"].sudo().browse(vehicle_id)
        if not vehicle.exists() or not vehicle.active:
            return False
        if not vehicle.website_published and request.env.user._is_public():
            return False
        return vehicle

    def _get_public_brand(self, brand_id):
        brand = request.env["auto.brand"].sudo().browse(brand_id)
        if not brand.exists() or not brand.active:
            return False
        if not brand.website_published and request.env.user._is_public():
            return False
        return brand

    def _build_vehicle_domain(self, query):
        domain = [("active", "=", True), ("website_published", "=", True)]

        search = (query.get("search") or "").strip()
        if search:
            domain += ["|", ("name", "ilike", search), ("brand_id.name", "ilike", search)]

        brand_id = self._parse_int(query.get("brand"))
        if brand_id:
            domain.append(("brand_id", "=", brand_id))
        category_id = self._parse_int(query.get("category"))
        if category_id:
            domain.append(("category_id", "=", category_id))
        motorization_id = self._parse_int(query.get("motorization"))
        if motorization_id:
            domain.append(("motorization_id", "=", motorization_id))
        if query.get("availability"):
            domain.append(("availability", "=", query["availability"]))

        year_min = self._parse_int(query.get("year_min"))
        year_max = self._parse_int(query.get("year_max"))
        year_min, year_max = self._normalize_range(year_min, year_max)
        if year_min:
            domain.append(("year", ">=", year_min))
        if year_max:
            domain.append(("year", "<=", year_max))

        price_min = self._parse_float(query.get("price_min"))
        price_max = self._parse_float(query.get("price_max"))
        price_min, price_max = self._normalize_range(price_min, price_max)
        if price_min is not None:
            domain.append(("product_template_id.list_price", ">=", price_min))
        if price_max is not None:
            domain.append(("product_template_id.list_price", "<=", price_max))

        return domain

    def _get_price_bounds(self):
        vehicles = request.env["auto.vehicle"].sudo().search(
            [("active", "=", True), ("website_published", "=", True)]
        )
        prices = [vehicle.list_price for vehicle in vehicles if vehicle.list_price > 0]
        if not prices:
            return 0, 100000
        price_floor = int(math.floor(min(prices) / 1000.0) * 1000)
        price_ceiling = int(math.ceil(max(prices) / 1000.0) * 1000)
        if price_floor == price_ceiling:
            price_ceiling += 1000
        return price_floor, price_ceiling

    def _get_catalog_order(self, sort_key):
        sort_map = {
            "newest": "id desc",
            "price_asc": "product_template_id.list_price asc",
            "price_desc": "product_template_id.list_price desc",
            "range_desc": "range_km desc",
            "year_desc": "year desc",
        }
        return sort_map.get(sort_key or "newest", "id desc")

    @http.route("/shop", type="http", auth="public", website=True, sitemap=False)
    def shop_redirect(self, **kwargs):
        return request.redirect("/cars")

    @http.route(["/cars", "/cars/page/<int:page>"], type="http", auth="public", website=True, sitemap=True)
    def cars_catalog(self, page=1, **kwargs):
        vehicle_model = request.env["auto.vehicle"].sudo()
        brand_model = request.env["auto.brand"].sudo()
        category_model = request.env["auto.vehicle.category"].sudo()
        motorization_model = request.env["auto.motorization"].sudo()

        domain = self._build_vehicle_domain(kwargs)
        order = self._get_catalog_order(kwargs.get("sort"))
        price_floor, price_ceiling = self._get_price_bounds()
        selected_price_min = self._parse_float(kwargs.get("price_min"))
        selected_price_max = self._parse_float(kwargs.get("price_max"))
        selected_price_min, selected_price_max = self._normalize_range(
            selected_price_min,
            selected_price_max,
        )
        selected_year_min = self._parse_int(kwargs.get("year_min"))
        selected_year_max = self._parse_int(kwargs.get("year_max"))
        selected_year_min, selected_year_max = self._normalize_range(
            selected_year_min,
            selected_year_max,
        )

        total = vehicle_model.search_count(domain)
        pager = request.website.pager(
            url="/cars",
            total=total,
            page=page,
            step=12,
            scope=5,
            url_args=kwargs,
        )
        vehicles = vehicle_model.search(domain, limit=12, offset=pager["offset"], order=order)

        values = {
            "additional_title": _("Catalogue automobile"),
            "vehicles": vehicles,
            "brands": brand_model.search([("active", "=", True)], order="sequence,name"),
            "categories": category_model.search([("active", "=", True)], order="sequence,name"),
            "motorizations": motorization_model.search([("active", "=", True)], order="sequence,name"),
            "pager": pager,
            "query": kwargs,
            "sort_key": kwargs.get("sort", "newest"),
            "price_floor": price_floor,
            "price_ceiling": price_ceiling,
            "selected_price_min": selected_price_min if selected_price_min is not None else price_floor,
            "selected_price_max": selected_price_max if selected_price_max is not None else price_ceiling,
            "selected_year_min": selected_year_min,
            "selected_year_max": selected_year_max,
            "availability_values": vehicle_model._fields["availability"]._description_selection(
                request.env
            ),
        }
        return request.render("auto_website.catalog_page", values)

    @http.route(["/cars/<int:vehicle_id>"], type="http", auth="public", website=True, sitemap=True)
    def car_detail(self, vehicle_id, **kwargs):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()

        review_model = request.env["auto.review"].sudo() if "auto.review" in request.env else False
        reviews = review_model.search(
            [("vehicle_id", "=", vehicle.id), ("state", "=", "approved")], order="id desc"
        ) if review_model else []

        partner = request.env.user.partner_id if request.env.user and request.env.user.partner_id else False
        is_favorite = bool(partner and partner in vehicle.favorite_partner_ids)

        related = request.env["auto.vehicle"].sudo().search(
            [
                ("id", "!=", vehicle.id),
                ("brand_id", "=", vehicle.brand_id.id),
                ("website_published", "=", True),
                ("active", "=", True),
            ],
            limit=3,
        )

        values = {
            "vehicle": vehicle,
            "related_vehicles": related,
            "reviews": reviews,
            "is_favorite": is_favorite,
        }
        return request.render("auto_website.vehicle_detail_page", values)

    @http.route("/cars/home", type="http", auth="public", website=True, sitemap=True)
    def cars_home(self, **kwargs):
        vehicle_model = request.env["auto.vehicle"].sudo()
        brand_model = request.env["auto.brand"].sudo()
        category_model = request.env["auto.vehicle.category"].sudo()

        public_domain = [("website_published", "=", True), ("active", "=", True)]
        featured_domain = public_domain + [("featured", "=", True)]

        featured = vehicle_model.search(featured_domain, limit=8, order="year desc, id desc")
        if not featured:
            featured = vehicle_model.search(public_domain, limit=8, order="year desc, id desc")

        hero_vehicles = featured[:3]
        latest_vehicles = vehicle_model.search(public_domain, limit=6, order="year desc, id desc")
        brands = brand_model.search(
            [("website_published", "=", True), ("active", "=", True)], order="sequence,name"
        )
        categories = category_model.search([("active", "=", True)], order="sequence,name")

        if hasattr(vehicle_model, "formatted_read_group"):
            category_group = vehicle_model.formatted_read_group(
                public_domain, ["category_id"], ["__count"]
            )
        else:
            category_group = vehicle_model.read_group(
                public_domain, ["category_id"], ["category_id"], lazy=False
            )
        category_count_map = {}
        for row in category_group:
            if not row.get("category_id"):
                continue
            count = row.get("category_id_count", row.get("__count", 0))
            category_count_map[row["category_id"][0]] = count

        available_count = vehicle_model.search_count(public_domain + [("availability", "=", "available")])
        priced_vehicles = vehicle_model.search(public_domain)
        starting_vehicle = priced_vehicles.filtered(lambda v: v.list_price > 0).sorted("list_price")[:1]

        return request.render(
            "auto_website.home_page",
            {
                "additional_title": _("Accueil automobile"),
                "featured_vehicles": featured,
                "hero_vehicles": hero_vehicles,
                "latest_vehicles": latest_vehicles,
                "brands": brands,
                "categories": categories,
                "category_count_map": category_count_map,
                "vehicle_total": vehicle_model.search_count(public_domain),
                "available_count": available_count,
                "starting_vehicle": starting_vehicle,
                "carousel_indicator_label": _("Indicateur du carrousel"),
            },
        )

    @http.route("/brands", type="http", auth="public", website=True, sitemap=True)
    def brand_list(self, **kwargs):
        brands = request.env["auto.brand"].sudo().search(
            [("website_published", "=", True), ("active", "=", True)], order="sequence,name"
        )
        return request.render(
            "auto_website.brand_list_page",
            {"additional_title": _("Marques automobiles"), "brands": brands},
        )

    @http.route("/brands/<int:brand_id>", type="http", auth="public", website=True, sitemap=True)
    def brand_detail(self, brand_id, **kwargs):
        brand = self._get_public_brand(brand_id)
        if not brand:
            return request.not_found()
        vehicles = request.env["auto.vehicle"].sudo().search(
            [
                ("brand_id", "=", brand.id),
                ("website_published", "=", True),
                ("active", "=", True),
            ],
            order="featured desc, id desc",
        )
        return request.render(
            "auto_website.brand_detail_page",
            {"brand": brand, "vehicles": vehicles},
        )

    @http.route(
        "/cars/cart/add",
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=True,
    )
    def add_car_to_cart(self, product_id=None, add_qty=1, **kwargs):
        """Add a vehicle variant to the cart across supported Odoo versions."""
        try:
            product_id = int(product_id or 0)
            quantity = max(int(float(add_qty or 1)), 1)
        except (TypeError, ValueError):
            return request.redirect("/cars")

        product = request.env["product.product"].sudo().browse(product_id).exists()
        if not product:
            return request.redirect("/cars")
        if hasattr(product, "_is_add_to_cart_allowed") and not product._is_add_to_cart_allowed():
            return request.redirect("/cars")

        cart = getattr(request, "cart", False)
        if not cart:
            if hasattr(request.website, "_create_cart"):
                cart = request.website._create_cart()
            else:
                cart = request.website.sale_get_order(force_create=True)

        if hasattr(cart, "_cart_add"):
            cart.with_context(skip_cart_verification=True)._cart_add(
                product_id=product.id,
                quantity=quantity,
            )
        else:
            cart._cart_update(product_id=product.id, add_qty=quantity)

        return request.redirect("/shop/cart")

    @http.route("/cars/favorite/<int:vehicle_id>", type="http", auth="user", methods=["POST"], website=True, csrf=True)
    def toggle_favorite(self, vehicle_id, **kwargs):
        vehicle = request.env["auto.vehicle"].sudo().browse(vehicle_id)
        if vehicle.exists():
            vehicle.with_user(request.env.user).action_toggle_favorite()
        return request.redirect(request.httprequest.referrer or "/cars")

    @http.route("/my/favorites", type="http", auth="user", website=True)
    def my_favorites(self, **kwargs):
        partner = request.env.user.partner_id
        favorites = request.env["auto.vehicle"].sudo().search(
            [("favorite_partner_ids", "in", partner.id)], order="id desc"
        )
        return request.render(
            "auto_website.my_favorites_page",
            {"additional_title": _("Véhicules favoris"), "vehicles": favorites},
        )
