from odoo import fields, models


class AutoFinancingRequest(models.Model):
    _name = "auto.financing.request"
    _description = "Demande de financement véhicule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    STATE_SELECTION = [
        ("new", "Nouvelle"),
        ("under_review", "En étude"),
        ("approved", "Approuvée"),
        ("rejected", "Rejetée"),
    ]

    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    vehicle_id = fields.Many2one("auto.vehicle", required=True, tracking=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    requested_amount = fields.Monetary(required=True, currency_field="currency_id")
    duration_months = fields.Integer(required=True, default=36)
    monthly_income = fields.Monetary(currency_field="currency_id")
    down_payment = fields.Monetary(currency_field="currency_id")
    note = fields.Text()
    state = fields.Selection(STATE_SELECTION, default="new", tracking=True)
    assigned_user_id = fields.Many2one("res.users", string="Conseiller assigné")

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)

    def action_mark_under_review(self):
        self.write({"state": "under_review"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_reject(self):
        self.write({"state": "rejected"})
