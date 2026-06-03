from odoo import _, fields, http
from odoo.http import request


class AutoBookingController(http.Controller):
    def _get_public_vehicle(self, vehicle_id):
        vehicle = request.env["auto.vehicle"].sudo().browse(vehicle_id)
        if not vehicle.exists() or not vehicle.active:
            return False
        if not vehicle.website_published and request.env.user._is_public():
            return False
        return vehicle

    def _normalize_datetime(self, value):
        if not value:
            return False
        clean = value.replace("T", " ").strip()
        if len(clean) == 16:
            clean += ":00"
        return clean

    def _get_or_create_partner(self, name, email, phone):
        if not request.env.user._is_public():
            return request.env.user.partner_id
        partner = request.env["res.partner"].sudo().search([("email", "=", email)], limit=1)
        if partner:
            return partner
        return request.env["res.partner"].sudo().create(
            {
                "name": name,
                "email": email,
                "phone": phone,
                "type": "contact",
            }
        )

    @http.route(
        ["/cars/<int:vehicle_id>/book"],
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
        csrf=True,
    )
    def reserve_vehicle(self, vehicle_id, **post):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        slot_model = request.env["auto.appointment.slot"].sudo()
        slots = slot_model.search(
            [("start_datetime", ">=", fields.Datetime.now()), ("is_available", "=", True)],
            limit=25,
            order="start_datetime",
        )

        if request.httprequest.method == "POST":
            name = (post.get("name") or "").strip()
            email = (post.get("email") or "").strip()
            phone = (post.get("phone") or "").strip()
            if not name or not email:
                return request.render(
                    "auto_booking.booking_form_page",
                    {
                        "additional_title": _("Réservation automobile"),
                        "vehicle": vehicle,
                        "slots": slots,
                        "error": _("Le nom et l'email sont obligatoires."),
                        "post": post,
                    },
                )

            slot = False
            requested_datetime = self._normalize_datetime(post.get("requested_datetime"))
            if post.get("slot_id"):
                slot = slot_model.browse(int(post["slot_id"]))
                requested_datetime = slot.start_datetime

            if not requested_datetime:
                return request.render(
                    "auto_booking.booking_form_page",
                    {
                        "additional_title": _("Réservation automobile"),
                        "vehicle": vehicle,
                        "slots": slots,
                        "error": _("Sélectionnez un créneau ou indiquez une date souhaitée."),
                        "post": post,
                    },
                )

            partner = self._get_or_create_partner(name, email, phone)
            booking = request.env["auto.booking"].sudo().create(
                {
                    "partner_id": partner.id,
                    "vehicle_id": vehicle.id,
                    "requested_datetime": requested_datetime,
                    "slot_id": slot.id if slot else False,
                    "email": email,
                    "phone": phone,
                    "note": post.get("note"),
                    "source": "website",
                }
            )
            return request.redirect(f"/cars/{vehicle.id}/book/thanks?booking_id={booking.id}")

        return request.render(
            "auto_booking.booking_form_page",
            {
                "additional_title": _("Réservation automobile"),
                "vehicle": vehicle,
                "slots": slots,
                "post": {},
            },
        )

    @http.route(["/cars/<int:vehicle_id>/book/thanks"], type="http", auth="public", website=True)
    def reserve_vehicle_thanks(self, vehicle_id, booking_id=None, **kwargs):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        booking = request.env["auto.booking"].sudo().browse(int(booking_id)) if booking_id else False
        return request.render(
            "auto_booking.booking_thanks_page",
            {
                "additional_title": _("Confirmation de la réservation"),
                "vehicle": vehicle,
                "booking": booking,
            },
        )

    @http.route(
        ["/cars/<int:vehicle_id>/test-drive"],
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
        csrf=True,
    )
    def request_test_drive(self, vehicle_id, **post):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        slot_model = request.env["auto.appointment.slot"].sudo()
        slots = slot_model.search(
            [("start_datetime", ">=", fields.Datetime.now()), ("is_available", "=", True)],
            limit=25,
            order="start_datetime",
        )

        if request.httprequest.method == "POST":
            name = (post.get("name") or "").strip()
            email = (post.get("email") or "").strip()
            phone = (post.get("phone") or "").strip()
            if not name or not email:
                return request.render(
                    "auto_booking.test_drive_form_page",
                    {
                        "additional_title": _("Essai automobile"),
                        "vehicle": vehicle,
                        "slots": slots,
                        "error": _("Le nom et l'email sont obligatoires."),
                        "post": post,
                        "default_location": _("Showroom principal"),
                    },
                )

            slot = False
            requested_datetime = self._normalize_datetime(post.get("requested_datetime"))
            if post.get("slot_id"):
                slot = slot_model.browse(int(post["slot_id"]))
                requested_datetime = slot.start_datetime

            if not requested_datetime:
                return request.render(
                    "auto_booking.test_drive_form_page",
                    {
                        "additional_title": _("Essai automobile"),
                        "vehicle": vehicle,
                        "slots": slots,
                        "error": _("Sélectionnez un créneau ou indiquez une date souhaitée."),
                        "post": post,
                        "default_location": _("Showroom principal"),
                    },
                )

            partner = self._get_or_create_partner(name, email, phone)
            test_drive = request.env["auto.test.drive"].sudo().create(
                {
                    "partner_id": partner.id,
                    "vehicle_id": vehicle.id,
                    "requested_datetime": requested_datetime,
                    "slot_id": slot.id if slot else False,
                    "location": post.get("location") or _("Showroom principal"),
                    "email": email,
                    "phone": phone,
                    "comment": post.get("comment"),
                }
            )
            return request.redirect(f"/cars/{vehicle.id}/test-drive/thanks?test_drive_id={test_drive.id}")

        return request.render(
            "auto_booking.test_drive_form_page",
            {
                "additional_title": _("Essai automobile"),
                "vehicle": vehicle,
                "slots": slots,
                "post": {},
                "default_location": _("Showroom principal"),
            },
        )

    @http.route(
        ["/cars/<int:vehicle_id>/test-drive/thanks"],
        type="http",
        auth="public",
        website=True,
    )
    def test_drive_thanks(self, vehicle_id, test_drive_id=None, **kwargs):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        test_drive = (
            request.env["auto.test.drive"].sudo().browse(int(test_drive_id)) if test_drive_id else False
        )
        return request.render(
            "auto_booking.test_drive_thanks_page",
            {
                "additional_title": _("Confirmation de l'essai"),
                "vehicle": vehicle,
                "test_drive": test_drive,
            },
        )

    @http.route("/my/bookings", type="http", auth="user", website=True)
    def my_bookings(self, **kwargs):
        bookings = request.env["auto.booking"].sudo().search(
            [("partner_id", "=", request.env.user.partner_id.id)], order="requested_datetime desc"
        )
        return request.render(
            "auto_booking.my_bookings_page",
            {"additional_title": _("Réservations client"), "bookings": bookings},
        )

    @http.route("/my/test-drives", type="http", auth="user", website=True)
    def my_test_drives(self, **kwargs):
        test_drives = request.env["auto.test.drive"].sudo().search(
            [("partner_id", "=", request.env.user.partner_id.id)], order="requested_datetime desc"
        )
        return request.render(
            "auto_booking.my_test_drives_page",
            {"additional_title": _("Essais client"), "test_drives": test_drives},
        )
