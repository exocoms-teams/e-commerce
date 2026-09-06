# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super().session_info()
        ICP = self.env["ir.config_parameter"].sudo()
        name = ICP.get_param("debranding.name") or "EXOCOMS"
        url = ICP.get_param("debranding.url") or ""
        doc_url = ICP.get_param("debranding.documentation_url") or ""
        support_url = ICP.get_param("debranding.support_url") or ""

        result["debranding"] = {
            "name": name,
            "url": url,
            "documentation_url": doc_url,
            "support_url": support_url,
        }
        # Lien natif consommé par le webclient.
        result["support_url"] = support_url or url or ""

        hide_version = ICP.get_param("debranding.hide_version") in ("True", "true", "1")
        if hide_version and not self.env.user.has_group("base.group_system"):
            result["server_version"] = name
        return result
