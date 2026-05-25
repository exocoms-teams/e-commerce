from odoo import api, fields, models


class AutoBooking(models.Model):
    _name = "auto.booking"
    _description = "Vehicle Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_datetime desc, id desc"

    STATE_SELECTION = [
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("done", "Done"),
    ]

    name = fields.Char(default="New", readonly=True, copy=False)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    vehicle_id = fields.Many2one("auto.vehicle", required=True, tracking=True)
    requested_datetime = fields.Datetime(required=True, tracking=True)
    slot_id = fields.Many2one("auto.appointment.slot", tracking=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    source = fields.Selection(
        [("website", "Website"), ("phone", "Phone"), ("showroom", "Showroom")],
        default="website",
    )
    note = fields.Text()
    assigned_user_id = fields.Many2one("res.users", string="Assigned Advisor", tracking=True)
    state = fields.Selection(STATE_SELECTION, default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = seq.next_by_code("auto.booking") or "New"
        records = super().create(vals_list)
        template = self.env.ref("auto_booking.mail_template_booking_received", raise_if_not_found=False)
        for booking in records:
            if template and booking.email:
                template.send_mail(booking.id, force_send=True)
        return records

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_done(self):
        self.write({"state": "done"})
