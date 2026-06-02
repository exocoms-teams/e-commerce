from odoo import api, fields, models


class AutoReview(models.Model):
    _name = "auto.review"
    _description = "Avis client véhicule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    STATE_SELECTION = [
        ("pending", "En attente"),
        ("approved", "Approuvé"),
        ("rejected", "Rejeté"),
    ]

    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    vehicle_id = fields.Many2one("auto.vehicle", required=True, tracking=True)
    title = fields.Char(required=True)
    comment = fields.Text(required=True)
    rating = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")],
        required=True,
        default="5",
    )
    state = fields.Selection(STATE_SELECTION, default="pending", tracking=True)
    approved_by = fields.Many2one("res.users", readonly=True)
    approved_date = fields.Datetime(readonly=True)

    _sql_constraints = [
        (
            "auto_review_unique_partner_vehicle",
            "unique(partner_id, vehicle_id)",
            "Un client ne peut déposer qu'un seul avis par véhicule.",
        )
    ]

    def action_approve(self):
        self.write(
            {
                "state": "approved",
                "approved_by": self.env.user.id,
                "approved_date": fields.Datetime.now(),
            }
        )

    def action_reject(self):
        self.write({"state": "rejected", "approved_by": self.env.user.id})
