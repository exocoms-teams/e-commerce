from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound


class WinnersNavigationController(http.Controller):
    """Additional destinations for the Winners sidebar."""

    def _check_website(self):
        if not request.website or request.website.name != "Winners":
            raise NotFound()

    @http.route(
        "/publicites",
        type="http",
        auth="user",
        website=True,
        methods=["GET"],
    )
    def advertisements(self, page="1", **kwargs):
        self._check_website()

        try:
            page_number = max(1, int(page))
        except (TypeError, ValueError):
            page_number = 1

        ad_model = request.env["trend.ad"]
        page_size = 24
        total = ad_model.search_count([])
        last_page = max(1, (total + page_size - 1) // page_size)
        page_number = min(page_number, last_page)

        ads = ad_model.search(
            [],
            order="collected_at desc, id desc",
            limit=page_size,
            offset=(page_number - 1) * page_size,
        )

        network_labels = dict(
            ad_model.fields_get(["social_network"])
            ["social_network"]["selection"]
        )

        return request.render(
            "produits_tendance.template_advertisement_list",
            {
                "ads": ads,
                "network_labels": network_labels,
                "total": total,
                "page_number": page_number,
                "last_page": last_page,
            },
        )

    @http.route(
        "/sources",
        type="http",
        auth="user",
        website=True,
        methods=["GET"],
    )
    def sources(self, **kwargs):
        self._check_website()

        product_model = request.env["trend.product"]
        ad_model = request.env["trend.ad"]

        product_sources = product_model.fields_get(["source"])
        networks = ad_model.fields_get(["social_network"])

        source_counts = [
            {
                "label": label,
                "count": product_model.search_count([
                    ("source", "=", value),
                ]),
            }
            for value, label in product_sources["source"]["selection"]
        ]

        network_counts = [
            {
                "label": label,
                "count": ad_model.search_count([
                    ("social_network", "=", value),
                ]),
            }
            for value, label in networks["social_network"]["selection"]
        ]

        return request.render(
            "produits_tendance.template_source_overview",
            {
                "source_counts": source_counts,
                "network_counts": network_counts,
            },
        )