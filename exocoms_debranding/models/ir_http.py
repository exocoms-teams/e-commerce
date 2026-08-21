# -*- coding: utf-8 -*-
from odoo import models

FALSY = ("False", "false", "0", "", "None")


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super().session_info()
        icp = self.env["ir.config_parameter"].sudo()
        company = self.env.company
        master = icp.get_param("exocoms_debranding.enabled", "True") not in FALSY
        result["exocoms_debranding"] = bool(master and company and company.debrand_backend)
        result["exocoms_brand_name"] = company._debrand_name() if company else "EXOCOMS"
        return result
