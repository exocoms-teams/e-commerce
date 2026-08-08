# -*- coding: utf-8 -*-
import base64
import io

from odoo import http
from odoo.http import request
from odoo.tools.image import guess_mimetype


class ExocomsBrandController(http.Controller):
    """Sert le logo de marque en accès public.

    Indispensable : le logo est référencé par une URL absolue dans les e-mails
    et les PDF, qui sont consultés hors session (client final, imprimante...).
    """

    @http.route(
        "/exocoms_brand/logo",
        type="http",
        auth="public",
        methods=["GET"],
        website=False,
    )
    def brand_logo(self, company=None, unique=None, **kwargs):
        Company = request.env["res.company"].sudo()
        record = None
        if company:
            try:
                record = Company.browse(int(company)).exists()
            except (TypeError, ValueError):
                record = None
        if not record:
            record = request.env.company.sudo()

        if not record or not record.debrand_logo:
            # Repli : le logo standard de la société.
            return request.redirect("/logo.png", local=True)

        content = base64.b64decode(record.debrand_logo)
        headers = [
            ("Content-Type", guess_mimetype(content, default="image/png")),
            ("Content-Length", len(content)),
            ("Cache-Control", "public, max-age=%d" % (60 * 60 * 24 if unique else 300)),
        ]
        return request.make_response(content, headers)
