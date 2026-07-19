from odoo import http
from odoo.http import request


class InstallersController(http.Controller):

    @http.route("/installers", auth="public", website=True)
    def installers_page(self, **kw):

        tire_categories = (
            request.env["product.category"]
            .sudo()
            .search(
                [
                    ("tire_category", "!=", False),
                ],
                order="sequence, name",
            )
        )

        return request.render(
            "tire_catalog.installers_page",
            {
                "tire_categories": tire_categories,
            },
        )

    @http.route(
        "/installers/submit",
        type="http",
        auth="public",
        website=True,
        csrf=True,
        methods=["POST"],
    )
    def installers_submit(self, **post):

        vals = {
            "company": post.get("company"),
            "name": post.get("name"),
            "email": post.get("email"),
            "phone": post.get("phone"),
            "address": post.get("address"),
        }

        request.env["tire.installer"].sudo().create(vals)

        return request.redirect("/installers/thanks")

    @http.route("/installers/thanks", auth="public", website=True)
    def installers_thanks(self, **kw):
        return request.render("tire_catalog.installers_thanks")
