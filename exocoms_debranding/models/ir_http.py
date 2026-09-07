# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super().session_info()
        # Société active de l'utilisateur : le backend suit le sélecteur
        # de société en haut à droite.
        branding = self.env.company.sudo()._debranding_values()

        result["debranding"] = {
            "name": branding["name"],
            "url": branding["url"],
            "documentation_url": branding["documentation_url"],
            "support_url": branding["support_url"],
            "logo": branding["logo"],
        }
        # Lien natif consommé par le webclient.
        result["support_url"] = branding["support_url"] or branding["url"] or ""

        ICP = self.env["ir.config_parameter"].sudo()
        hide_version = ICP.get_param("debranding.hide_version") in ("True", "true", "1")
        if hide_version and not self.env.user.has_group("base.group_system"):
            result["server_version"] = branding["name"]
        return result
