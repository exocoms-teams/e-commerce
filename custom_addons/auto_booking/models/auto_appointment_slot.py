from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AutoAppointmentSlot(models.Model):
    _name = "auto.appointment.slot"
    _description = "Appointment Slot"
    _order = "start_datetime"

    name = fields.Char(compute="_compute_name", store=True)
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)
    capacity = fields.Integer(default=1)
    active = fields.Boolean(default=True)
    booking_ids = fields.One2many("auto.booking", "slot_id")
    test_drive_ids = fields.One2many("auto.test.drive", "slot_id")
    occupied_count = fields.Integer(compute="_compute_occupied_count", store=True)
    is_available = fields.Boolean(compute="_compute_occupied_count", store=True)

    @api.depends("start_datetime", "end_datetime")
    def _compute_name(self):
        for slot in self:
            if slot.start_datetime and slot.end_datetime:
                slot.name = _("%s to %s") % (
                    fields.Datetime.to_string(slot.start_datetime),
                    fields.Datetime.to_string(slot.end_datetime),
                )
            else:
                slot.name = _("New Slot")

    @api.depends("booking_ids.state", "test_drive_ids.state", "capacity")
    def _compute_occupied_count(self):
        for slot in self:
            bookings = len(slot.booking_ids.filtered(lambda r: r.state in ("draft", "confirmed")))
            tests = len(slot.test_drive_ids.filtered(lambda r: r.state in ("draft", "confirmed")))
            slot.occupied_count = bookings + tests
            slot.is_available = slot.occupied_count < slot.capacity

    @api.constrains("start_datetime", "end_datetime", "capacity")
    def _check_slot(self):
        for slot in self:
            if slot.end_datetime <= slot.start_datetime:
                raise ValidationError(_("End datetime must be greater than start datetime."))
            if slot.capacity < 1:
                raise ValidationError(_("Capacity must be at least 1."))
