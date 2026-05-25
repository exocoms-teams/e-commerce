from odoo import http
from odoo.http import request


class AutoReviewController(http.Controller):
    def _get_public_vehicle(self, vehicle_id):
        vehicle = request.env["auto.vehicle"].sudo().browse(vehicle_id)
        if not vehicle.exists() or not vehicle.active:
            return False
        if not vehicle.website_published and request.env.user._is_public():
            return False
        return vehicle

    @http.route(
        "/cars/<int:vehicle_id>/review",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def submit_review(self, vehicle_id, **post):
        vehicle = self._get_public_vehicle(vehicle_id)
        if not vehicle:
            return request.not_found()
        title = (post.get("title") or "").strip()
        comment = (post.get("comment") or "").strip()
        rating = str(post.get("rating") or "5")

        if not title or not comment or rating not in {"1", "2", "3", "4", "5"}:
            return request.redirect(request.httprequest.referrer or vehicle.website_url)

        review_model = request.env["auto.review"].sudo()
        existing = review_model.search(
            [
                ("partner_id", "=", request.env.user.partner_id.id),
                ("vehicle_id", "=", vehicle.id),
            ],
            limit=1,
        )

        values = {
            "partner_id": request.env.user.partner_id.id,
            "vehicle_id": vehicle.id,
            "title": title,
            "comment": comment,
            "rating": rating,
            "state": "pending",
        }

        if existing:
            existing.write(values)
        else:
            review_model.create(values)

        return request.redirect(request.httprequest.referrer or vehicle.website_url)

    @http.route("/my/reviews", type="http", auth="user", website=True)
    def my_reviews(self, **kwargs):
        reviews = request.env["auto.review"].sudo().search(
            [("partner_id", "=", request.env.user.partner_id.id)], order="id desc"
        )
        return request.render("auto_reviews.my_reviews_page", {"reviews": reviews})
