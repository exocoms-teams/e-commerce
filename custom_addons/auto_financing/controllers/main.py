from odoo import http
from odoo.http import request


class AutoFinancingController(http.Controller):
    def _get_public_vehicle(self, vehicle_id):
        vehicle = request.env["auto.vehicle"].sudo().browse(vehicle_id)
        if not vehicle.exists() or not vehicle.active:
            return False
        if not vehicle.website_published and request.env.user._is_public():
            return False
        return vehicle

    @http.route(
        ["/cars/<int:vehicle_id>/financing"],
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
        csrf=True,
    )
    def financing_request(self, vehicle_id, **post):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        if request.httprequest.method == "POST":
            name = (post.get("name") or "").strip()
            email = (post.get("email") or "").strip()
            phone = (post.get("phone") or "").strip()
            if not name or not email:
                return request.render(
                    "auto_financing.financing_form_page",
                    {"vehicle": vehicle, "post": post, "error": "Le nom et l'email sont obligatoires."},
                )

            partner = request.env.user.partner_id
            if request.env.user._is_public():
                partner = request.env["res.partner"].sudo().search([("email", "=", email)], limit=1)
                if not partner:
                    partner = request.env["res.partner"].sudo().create(
                        {"name": name, "email": email, "phone": phone, "type": "contact"}
                    )

            req = request.env["auto.financing.request"].sudo().create(
                {
                    "partner_id": partner.id,
                    "vehicle_id": vehicle.id,
                    "email": email,
                    "phone": phone,
                    "requested_amount": float(post.get("requested_amount") or 0),
                    "duration_months": int(post.get("duration_months") or 36),
                    "monthly_income": float(post.get("monthly_income") or 0),
                    "down_payment": float(post.get("down_payment") or 0),
                    "note": post.get("note"),
                }
            )
            return request.redirect(f"/cars/{vehicle.id}/financing/thanks?request_id={req.id}")

        return request.render("auto_financing.financing_form_page", {"vehicle": vehicle, "post": {}})

    @http.route(["/cars/<int:vehicle_id>/financing/thanks"], type="http", auth="public", website=True)
    def financing_thanks(self, vehicle_id, request_id=None, **kwargs):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        req = request.env["auto.financing.request"].sudo().browse(int(request_id)) if request_id else False
        return request.render("auto_financing.financing_thanks_page", {"vehicle": vehicle, "request_obj": req})

    @http.route("/my/financing-requests", type="http", auth="user", website=True)
    def my_financing_requests(self, **kwargs):
        records = request.env["auto.financing.request"].sudo().search(
            [("partner_id", "=", request.env.user.partner_id.id)], order="id desc"
        )
        return request.render("auto_financing.my_financing_requests_page", {"records": records})
