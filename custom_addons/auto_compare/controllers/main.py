from odoo import _, http
from odoo.http import request


class AutoCompareController(http.Controller):
    SESSION_KEY = "auto_compare_vehicle_ids"
    MAX_COMPARE = 4

    def _get_compare_ids(self):
        ids = request.session.get(self.SESSION_KEY, [])
        if not isinstance(ids, list):
            ids = []
        return [int(v) for v in ids if isinstance(v, int) or str(v).isdigit()]

    def _save_compare_ids(self, ids):
        request.session[self.SESSION_KEY] = ids

    @http.route("/cars/compare", type="http", auth="public", website=True, sitemap=True)
    def compare_page(self, **kwargs):
        vehicle_ids = self._get_compare_ids()
        vehicles = request.env["auto.vehicle"].sudo().search(
            [("id", "in", vehicle_ids), ("active", "=", True), ("website_published", "=", True)]
        )
        vehicles = vehicles.sorted(key=lambda v: vehicle_ids.index(v.id))
        return request.render(
            "auto_compare.compare_page",
            {"additional_title": _("Comparateur automobile"), "vehicles": vehicles},
        )

    @http.route("/cars/compare/add/<int:vehicle_id>", type="http", auth="public", website=True)
    def compare_add(self, vehicle_id, **kwargs):
        ids = self._get_compare_ids()
        if vehicle_id not in ids:
            ids.append(vehicle_id)
        ids = ids[: self.MAX_COMPARE]
        self._save_compare_ids(ids)
        return request.redirect(request.httprequest.referrer or "/cars/compare")

    @http.route("/cars/compare/remove/<int:vehicle_id>", type="http", auth="public", website=True)
    def compare_remove(self, vehicle_id, **kwargs):
        ids = self._get_compare_ids()
        ids = [vid for vid in ids if vid != vehicle_id]
        self._save_compare_ids(ids)
        return request.redirect(request.httprequest.referrer or "/cars/compare")

    @http.route("/cars/compare/clear", type="http", auth="public", website=True)
    def compare_clear(self, **kwargs):
        self._save_compare_ids([])
        return request.redirect("/cars/compare")
