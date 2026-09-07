# -*- coding: utf-8 -*-
"""Injection du dictionnaire ``debranding`` dans le contexte de rendu QWeb.

``ir.qweb._prepare_values`` est traversé par tous les rendus serveur : pages
backend, écran de connexion, portail, site web, layouts de courriels et
rapports. C'est le seul point unique permettant de résoudre la société au
moment du rendu.

Les templates OWL ne sont pas concernés : depuis Odoo 15 ils vivent dans les
bundles d'assets et non en base, donc hors du périmètre des patchs.
"""
import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrQweb(models.AbstractModel):
    _inherit = "ir.qweb"

    def _prepare_values(self, values, *args, **kwargs):
        values = super()._prepare_values(values, *args, **kwargs)
        try:
            if isinstance(values, dict) and "debranding" not in values:
                company = self._debranding_company(values)
                values["debranding"] = company._debranding_values()
        except Exception:  # noqa: BLE001 - ne doit jamais casser un rendu
            _logger.exception("Debranding : injection du contexte QWeb impossible.")
        return values

    def _debranding_company(self, values):
        """Résout la société pertinente pour ce rendu.

        Ordre : société explicite du contexte (rapports, courriels) -> site web
        -> enregistrement rendu -> société de la requête -> société de l'env.
        """
        Company = self.env["res.company"].sudo()

        candidates = [
            values.get("company"),
            values.get("res_company"),
            values.get("company_id"),
        ]

        website = values.get("website")
        if website is not None and hasattr(website, "company_id"):
            candidates.append(website.company_id)

        for key in ("record", "object", "doc"):
            record = values.get(key)
            if isinstance(record, models.BaseModel) and "company_id" in record._fields:
                candidates.append(record[:1].company_id)

        for candidate in candidates:
            if isinstance(candidate, models.BaseModel):
                if candidate._name == "res.company" and candidate:
                    return candidate[:1].sudo()
            elif isinstance(candidate, int) and candidate:
                return Company.browse(candidate)

        if request:
            try:
                return request.env.company.sudo()
            except Exception:  # noqa: BLE001
                pass
        return self.env.company.sudo()
