# -*- coding: utf-8 -*-
"""Rebranding du manifeste PWA (nom, icônes, couleurs).

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

            ICP = request.env["ir.config_parameter"].sudo()
            name = ICP.get_param("debranding.name") or "EXOCOMS"
            logo = ICP.get_param("debranding.logo_url") or "/logo.png"
            theme = ICP.get_param("debranding.theme_color") or ""

            manifest["name"] = ICP.get_param("web.web_app_name") or name
            manifest["short_name"] = name
            manifest["icons"] = [
                {
                    "src": logo,
                    "sizes": size,
                    "type": "image/png",
                    "purpose": "any",
                }
                for size in ("192x192", "512x512")
            ]
            if theme:
                manifest["theme_color"] = theme
                manifest["background_color"] = theme

            response.set_data(json.dumps(manifest))
            return response
