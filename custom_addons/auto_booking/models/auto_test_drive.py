from odoo import api, fields, models


class AutoTestDrive(models.Model):
    _name = "auto.test.drive"
    _description = "Essai de véhicule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_datetime desc, id desc"

    STATE_SELECTION = [
        ("draft", "Brouillon"),
        ("confirmed", "Confirmé"),
        ("cancelled", "Annulé"),
        ("done", "Terminé"),
    ]

    name = fields.Char(default="Nouveau", readonly=True, copy=False)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    vehicle_id = fields.Many2one("auto.vehicle", required=True, tracking=True)
    requested_datetime = fields.Datetime(required=True, tracking=True)
    slot_id = fields.Many2one("auto.appointment.slot", tracking=True)
    location = fields.Char(default="Showroom principal")
    email = fields.Char(required=True)
    phone = fields.Char()
    comment = fields.Text()
    assigned_user_id = fields.Many2one("res.users", string="Conseiller assigné", tracking=True)
    state = fields.Selection(STATE_SELECTION, default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "Nouveau") in ("New", "Nouveau"):
                vals["name"] = seq.next_by_code("auto.test.drive") or "Nouveau"
        records = super().create(vals_list)
        template = self.env.ref("auto_booking.mail_template_test_drive_received", raise_if_not_found=False)
        for test_drive in records:
            if template and test_drive.email:
                template.send_mail(test_drive.id, force_send=True)
        return records

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_done(self):
        self.write({"state": "done"})
