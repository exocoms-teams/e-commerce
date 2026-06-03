from odoo import _, http
from odoo.http import request


class AutoSaleController(http.Controller):
    def _get_public_vehicle(self, vehicle_id):
        vehicle = request.env["auto.vehicle"].sudo().browse(vehicle_id)
        if not vehicle.exists() or not vehicle.active:
            return False
        if not vehicle.website_published and request.env.user._is_public():
            return False
        return vehicle

    @http.route(
        ["/cars/<int:vehicle_id>/quote"],
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
        csrf=True,
    )
    def vehicle_quote_request(self, vehicle_id, **post):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        if request.httprequest.method == "POST":
            email = (post.get("email") or "").strip()
            full_name = (post.get("name") or "").strip()
            phone = (post.get("phone") or "").strip()

            if not email or not full_name:
                return request.render(
                    "auto_sale.quote_form_page",
                    {
                        "additional_title": _("Devis automobile"),
                        "vehicle": vehicle,
                        "error": _("Le nom et l'email sont obligatoires."),
                        "post": post,
                    },
                )

            partner = request.env.user.partner_id
            if request.env.user._is_public():
                partner = request.env["res.partner"].sudo().search(
                    [("email", "=", email)], limit=1
                )
                if not partner:
                    partner = request.env["res.partner"].sudo().create(
                        {
                            "name": full_name,
                            "email": email,
                            "phone": phone,
                            "type": "contact",
                        }
                    )

            quote_request = request.env["auto.quote.request"].sudo().create(
                {
                    "partner_id": partner.id,
                    "vehicle_id": vehicle.id,
                    "email": email,
                    "phone": phone,
                    "budget": float(post.get("budget") or 0),
                    "message": post.get("message"),
                    "preferred_contact": post.get("preferred_contact") or "email",
                    "source": "website",
                }
            )
            quote_request.action_create_lead()
            return request.redirect(f"/cars/{vehicle.id}/quote/thanks?request_id={quote_request.id}")

        return request.render(
            "auto_sale.quote_form_page",
            {
                "additional_title": _("Devis automobile"),
                "vehicle": vehicle,
                "post": {},
            },
        )

    @http.route(
        ["/cars/<int:vehicle_id>/quote/thanks"],
        type="http",
        auth="public",
        website=True,
    )
    def vehicle_quote_thanks(self, vehicle_id, request_id=None, **kwargs):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        quote_request = False
        if request_id:
            quote_request = request.env["auto.quote.request"].sudo().browse(int(request_id))
        return request.render(
            "auto_sale.quote_thanks_page",
            {
                "additional_title": _("Confirmation du devis"),
                "vehicle": vehicle,
                "quote_request": quote_request,
            },
        )
