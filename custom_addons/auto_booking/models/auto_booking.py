from odoo import api, fields, models


class AutoBooking(models.Model):
    _name = "auto.booking"
    _description = "Réservation de véhicule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_datetime desc, id desc"

    STATE_SELECTION = [
        ("draft", "Brouillon"),
        ("confirmed", "Confirmée"),
        ("cancelled", "Annulée"),
        ("done", "Terminée"),
    ]

    name = fields.Char(default="Nouveau", readonly=True, copy=False)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    vehicle_id = fields.Many2one("auto.vehicle", required=True, tracking=True)
    requested_datetime = fields.Datetime(required=True, tracking=True)
    slot_id = fields.Many2one("auto.appointment.slot", tracking=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    source = fields.Selection(
        [("website", "Site web"), ("phone", "Téléphone"), ("showroom", "Showroom")],
        default="website",
    )
    note = fields.Text()
    assigned_user_id = fields.Many2one("res.users", string="Conseiller assigné", tracking=True)
    state = fields.Selection(STATE_SELECTION, default="draft", tracking=True)
    state_label = fields.Char(compute="_compute_state_label")

    @api.depends("state")
    @api.depends_context("lang")
    def _compute_state_label(self):
        labels = dict(self._fields["state"]._description_selection(self.env))
        for booking in self:
            booking.state_label = labels.get(booking.state)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "Nouveau") in ("New", "Nouveau"):
                vals["name"] = seq.next_by_code("auto.booking") or "Nouveau"
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
