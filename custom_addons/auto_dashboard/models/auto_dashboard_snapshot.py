from datetime import date, timedelta

from odoo import api, fields, models


class AutoDashboardSnapshot(models.Model):
    _name = "auto.dashboard.snapshot"
    _description = "Instantané du tableau de bord automobile"
    _order = "create_date desc"

    name = fields.Char(default="Instantané du tableau de bord", required=True)
    date_from = fields.Date(default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(default=lambda self: date.today())

    orders_count = fields.Integer(compute="_compute_kpis")
    revenue_total = fields.Monetary(compute="_compute_kpis", currency_field="currency_id")
    quote_request_count = fields.Integer(compute="_compute_kpis")
    booking_count = fields.Integer(compute="_compute_kpis")
    test_drive_count = fields.Integer(compute="_compute_kpis")
    approved_review_count = fields.Integer(compute="_compute_kpis")
    published_vehicle_count = fields.Integer(compute="_compute_kpis")
    crm_opportunity_count = fields.Integer(compute="_compute_kpis")
    top_vehicle_id = fields.Many2one("auto.vehicle", compute="_compute_kpis")

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)

    def _date_domain(self):
        self.ensure_one()
        domain = []
        if self.date_from:
            start = fields.Datetime.to_datetime(self.date_from)
            domain.append(("create_date", ">=", start))
        if self.date_to:
            end = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)
            domain.append(("create_date", "<", end))
        return domain

    @api.depends("date_from", "date_to")
    def _compute_kpis(self):
        sale_order_model = self.env["sale.order"].sudo()
        quote_model = self.env["auto.quote.request"].sudo()
        booking_model = self.env["auto.booking"].sudo()
        test_drive_model = self.env["auto.test.drive"].sudo()
        review_model = self.env["auto.review"].sudo()
        vehicle_model = self.env["auto.vehicle"].sudo()
        crm_model = self.env["crm.lead"].sudo()

        for snapshot in self:
            domain = snapshot._date_domain()
            sale_domain = domain + [("state", "in", ["sale", "done"])]
            orders = sale_order_model.search(sale_domain)
            snapshot.orders_count = len(orders)
            snapshot.revenue_total = sum(orders.mapped("amount_total"))

            snapshot.quote_request_count = quote_model.search_count(domain)
            snapshot.booking_count = booking_model.search_count(domain)
            snapshot.test_drive_count = test_drive_model.search_count(domain)
            snapshot.approved_review_count = review_model.search_count(
                domain + [("state", "=", "approved")]
            )
            snapshot.published_vehicle_count = vehicle_model.search_count(
                [("website_published", "=", True), ("active", "=", True)]
            )
            snapshot.crm_opportunity_count = crm_model.search_count(
                domain + [("type", "=", "opportunity")]
            )

            top = self.env["sale.order.line"].sudo().read_group(
                sale_domain,
                ["auto_vehicle_id", "product_uom_qty:sum"],
                ["auto_vehicle_id"],
                limit=1,
                orderby="product_uom_qty desc",
            )
            snapshot.top_vehicle_id = top[0]["auto_vehicle_id"][0] if top and top[0]["auto_vehicle_id"] else False

    def action_refresh(self):
        return {"type": "ir.actions.client", "tag": "reload"}

