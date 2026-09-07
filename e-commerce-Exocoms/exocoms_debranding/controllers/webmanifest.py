# -*- coding: utf-8 -*-
"""Rebranding du manifeste PWA (nom, icônes, couleurs).

Les valeurs sont résolues sur la société de la requête : en multi-société avec
un site web par société, chaque site sert son propre manifeste.

L'override est défensif : si le contrôleur amont change de chemin d'import,
le module se charge quand même et le manifeste reste natif.
"""
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.web.controllers.webmanifest import WebManifest
except ImportError:  # pragma: no cover
    WebManifest = None
    _logger.warning(
        "Debranding : contrôleur web.WebManifest introuvable, "
        "le manifeste PWA n'est pas rebrandé."
    )


if WebManifest is not None:

    class DebrandingWebManifest(WebManifest):

        @http.route()
        def webmanifest(self, *args, **kwargs):
            response = super().webmanifest(*args, **kwargs)
            try:
                manifest = json.loads(response.get_data())
            except Exception:  # noqa: BLE001
                return response

            branding = request.env.company.sudo()._debranding_values()
            app_name = (
                request.env["ir.config_parameter"].sudo().get_param("web.web_app_name")
                or branding["name"]
            )

            manifest["name"] = app_name
            manifest["short_name"] = branding["name"]
            manifest["icons"] = [
                {
                    "src": branding["logo"],
                    "sizes": size,
                    "type": "image/png",
                    "purpose": "any",
                }
                for size in ("192x192", "512x512")
            ]
            if branding["theme_color"]:
                manifest["theme_color"] = branding["theme_color"]
                manifest["background_color"] = branding["theme_color"]

            response.set_data(json.dumps(manifest))
            return response
