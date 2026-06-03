from datetime import date, timedelta

from odoo import api, fields, models


class AutoDashboardSnapshot(models.Model):
    _name = "auto.dashboard.snapshot"
    _description = "Instantané du tableau de bord automobile"
    _order = "create_date desc"

    name = fields.Char(default="Pilotage automobile EXOCOMS", required=True)
    date_from = fields.Date(default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(default=lambda self: date.today())

    orders_count = fields.Integer(compute="_compute_kpis")
    revenue_total = fields.Monetary(compute="_compute_kpis", currency_field="currency_id")
    quote_request_count = fields.Integer(compute="_compute_kpis")
    new_quote_request_count = fields.Integer(compute="_compute_kpis")
    booking_count = fields.Integer(compute="_compute_kpis")
    test_drive_count = fields.Integer(compute="_compute_kpis")
    approved_review_count = fields.Integer(compute="_compute_kpis")
    pending_review_count = fields.Integer(compute="_compute_kpis")
    published_vehicle_count = fields.Integer(compute="_compute_kpis")
    vehicle_count = fields.Integer(compute="_compute_kpis")
    available_vehicle_count = fields.Integer(compute="_compute_kpis")
    reserved_vehicle_count = fields.Integer(compute="_compute_kpis")
    sold_vehicle_count = fields.Integer(compute="_compute_kpis")
    coming_soon_vehicle_count = fields.Integer(compute="_compute_kpis")
    featured_vehicle_count = fields.Integer(compute="_compute_kpis")
    unpublished_vehicle_count = fields.Integer(compute="_compute_kpis")
    stock_total_qty = fields.Integer(compute="_compute_kpis")
    brand_count = fields.Integer(compute="_compute_kpis")
    category_count = fields.Integer(compute="_compute_kpis")
    motorization_count = fields.Integer(compute="_compute_kpis")
    option_count = fields.Integer(compute="_compute_kpis")
    financing_request_count = fields.Integer(compute="_compute_kpis")
    pending_financing_request_count = fields.Integer(compute="_compute_kpis")
    crm_opportunity_count = fields.Integer(compute="_compute_kpis")
    top_vehicle_id = fields.Many2one("auto.vehicle", compute="_compute_kpis")

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)

    def _date_domain(self, field_name="create_date"):
        self.ensure_one()
        domain = []
        if self.date_from:
            start = fields.Datetime.to_datetime(self.date_from)
            domain.append((field_name, ">=", start))
        if self.date_to:
            end = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)
            domain.append((field_name, "<", end))
        return domain

    @api.depends("date_from", "date_to")
    def _compute_kpis(self):
        sale_order_model = self.env["sale.order"].sudo()
        quote_model = self.env["auto.quote.request"].sudo()
        booking_model = self.env["auto.booking"].sudo()
        test_drive_model = self.env["auto.test.drive"].sudo()
        review_model = self.env["auto.review"].sudo()
        vehicle_model = self.env["auto.vehicle"].sudo()
        brand_model = self.env["auto.brand"].sudo()
        category_model = self.env["auto.vehicle.category"].sudo()
        motorization_model = self.env["auto.motorization"].sudo()
        option_model = self.env["auto.vehicle.option"].sudo()
        financing_model = self.env["auto.financing.request"].sudo()
        crm_model = self.env["crm.lead"].sudo()
        sale_line_model = self.env["sale.order.line"].sudo()

        for snapshot in self:
            domain = snapshot._date_domain()
            sale_domain = domain + [("state", "in", ["sale", "done"])]
            orders = sale_order_model.search(sale_domain)

            snapshot.orders_count = len(orders)
            snapshot.revenue_total = sum(orders.mapped("amount_total"))
            snapshot.quote_request_count = quote_model.search_count(domain)
            snapshot.new_quote_request_count = quote_model.search_count(domain + [("state", "=", "new")])
            snapshot.booking_count = booking_model.search_count(domain)
            snapshot.test_drive_count = test_drive_model.search_count(domain)
            snapshot.approved_review_count = review_model.search_count(
                domain + [("state", "=", "approved")]
            )
            snapshot.pending_review_count = review_model.search_count(domain + [("state", "=", "pending")])
            snapshot.financing_request_count = financing_model.search_count(domain)
            snapshot.pending_financing_request_count = financing_model.search_count(
                domain + [("state", "in", ["new", "under_review"])]
            )

            active_vehicle_domain = [("active", "=", True)]
            snapshot.vehicle_count = vehicle_model.search_count(active_vehicle_domain)
            snapshot.published_vehicle_count = vehicle_model.search_count(
                active_vehicle_domain + [("website_published", "=", True)]
            )
            snapshot.unpublished_vehicle_count = vehicle_model.search_count(
                active_vehicle_domain + [("website_published", "=", False)]
            )
            snapshot.available_vehicle_count = vehicle_model.search_count(
                active_vehicle_domain + [("availability", "=", "available")]
            )
            snapshot.reserved_vehicle_count = vehicle_model.search_count(
                active_vehicle_domain + [("availability", "=", "reserved")]
            )
            snapshot.sold_vehicle_count = vehicle_model.search_count(
                active_vehicle_domain + [("availability", "=", "sold")]
            )
            snapshot.coming_soon_vehicle_count = vehicle_model.search_count(
                active_vehicle_domain + [("availability", "=", "coming_soon")]
            )
            snapshot.featured_vehicle_count = vehicle_model.search_count(
                active_vehicle_domain + [("featured", "=", True)]
            )
            snapshot.stock_total_qty = sum(vehicle_model.search(active_vehicle_domain).mapped("stock_qty"))
            snapshot.brand_count = brand_model.search_count([("active", "=", True)])
            snapshot.category_count = category_model.search_count([])
            snapshot.motorization_count = motorization_model.search_count([])
            snapshot.option_count = option_model.search_count([])
            snapshot.crm_opportunity_count = crm_model.search_count(
                domain + [("type", "=", "opportunity")]
            )

            line_domain = snapshot._date_domain("order_id.create_date") + [
                ("order_id.state", "in", ["sale", "done"]),
                ("auto_vehicle_id", "!=", False),
            ]
            if hasattr(sale_line_model, "formatted_read_group"):
                top = sale_line_model.formatted_read_group(
                    line_domain,
                    ["auto_vehicle_id"],
                    ["product_uom_qty:sum"],
                    limit=1,
                    order="product_uom_qty:sum desc",
                )
            else:
                top = sale_line_model.read_group(
                    line_domain,
                    ["auto_vehicle_id", "product_uom_qty:sum"],
                    ["auto_vehicle_id"],
                    limit=1,
                    orderby="product_uom_qty desc",
                )
            snapshot.top_vehicle_id = top[0]["auto_vehicle_id"][0] if top and top[0]["auto_vehicle_id"] else False

    def action_refresh(self):
        return {"type": "ir.actions.client", "tag": "reload"}

    def _open_action(self, xmlid, name, res_model, view_mode="kanban,list,form", domain=None, context=None):
        action_record = self.env.ref(xmlid, raise_if_not_found=False)
        if action_record:
            action = action_record.sudo().read()[0]
        else:
            action = {
                "type": "ir.actions.act_window",
                "name": name,
                "res_model": res_model,
                "view_mode": view_mode,
            }
        if domain is not None:
            action["domain"] = domain
        if context is not None:
            action["context"] = context
        return action

    def action_new_vehicle(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Nouveau véhicule",
            "res_model": "auto.vehicle",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_website_published": True,
                "default_availability": "available",
                "default_stock_qty": 1,
            },
        }

    def action_new_brand(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Nouvelle marque",
            "res_model": "auto.brand",
            "view_mode": "form",
            "target": "current",
            "context": {"default_website_published": True},
        }

    def action_open_vehicles(self):
        return self._open_action("auto_base.action_auto_vehicle", "Véhicules", "auto.vehicle")

    def action_open_available_vehicles(self):
        return self._open_action(
            "auto_base.action_auto_vehicle",
            "Véhicules disponibles",
            "auto.vehicle",
            domain=[("availability", "=", "available"), ("active", "=", True)],
        )

    def action_open_unpublished_vehicles(self):
        return self._open_action(
            "auto_base.action_auto_vehicle",
            "Véhicules non publiés",
            "auto.vehicle",
            domain=[("website_published", "=", False), ("active", "=", True)],
        )

    def action_open_brands(self):
        return self._open_action("auto_base.action_auto_brand", "Marques", "auto.brand")

    def action_open_categories(self):
        return self._open_action(
            "auto_base.action_auto_vehicle_category",
            "Catégories de véhicules",
            "auto.vehicle.category",
            view_mode="list,form",
        )

    def action_open_motorizations(self):
        return self._open_action(
            "auto_base.action_auto_motorization",
            "Motorisations",
            "auto.motorization",
            view_mode="list,form",
        )

    def action_open_options(self):
        return self._open_action(
            "auto_base.action_auto_vehicle_option",
            "Options de véhicules",
            "auto.vehicle.option",
            view_mode="list,form",
        )

    def action_open_quote_requests(self):
        return self._open_action(
            "auto_sale.action_auto_quote_request",
            "Demandes de devis",
            "auto.quote.request",
            view_mode="list,form",
        )

    def action_open_bookings(self):
        return self._open_action(
            "auto_booking.action_auto_booking",
            "Réservations",
            "auto.booking",
            view_mode="list,form",
        )

    def action_open_test_drives(self):
        return self._open_action(
            "auto_booking.action_auto_test_drive",
            "Essais",
            "auto.test.drive",
            view_mode="list,form",
        )

    def action_open_financing_requests(self):
        return self._open_action(
            "auto_financing.action_auto_financing_request",
            "Demandes de financement",
            "auto.financing.request",
            view_mode="list,form",
        )

    def action_open_reviews(self):
        return self._open_action(
            "auto_reviews.action_auto_review",
            "Avis clients",
            "auto.review",
            view_mode="list,form",
        )

    def action_open_website_catalog(self):
        return {
            "type": "ir.actions.act_url",
            "name": "Catalogue public",
            "url": "/cars",
            "target": "new",
        }
