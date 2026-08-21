# -*- coding: utf-8 -*-
import logging

from odoo import models

from ..tools.debrand import debrand_html

_logger = logging.getLogger(__name__)

FALSY = ("False", "false", "0", "", "None")


class IrQWeb(models.AbstractModel):
    """Point d'entrée unique de tous les rendus QWeb d'Odoo.

    Couvre : pages portail / site web, layouts d'e-mails de notification,
    templates de mail, rapports QWeb-HTML et QWeb-PDF (devis, factures, BL...).
    """

    _inherit = "ir.qweb"

    def _exocoms_debrand_enabled(self):
        if self.env.context.get("exocoms_skip_debrand"):
            return False
        try:
            value = self.env["ir.config_parameter"].sudo().get_param(
                "exocoms_debranding.enabled", "True"
            )
        except Exception:  # pragma: no cover - base non initialisée
            return False
        return value not in FALSY

    def _exocoms_debrand_params(self):
        """Retourne (snippet, generator) selon la société courante."""
        company = self.env.company
        if not company:
            return None, None
        return company._debrand_snippet(), company._debrand_name()

    def _render(self, *args, **kwargs):
        result = super()._render(*args, **kwargs)
        if not isinstance(result, str):
            return result
        if not self._exocoms_debrand_enabled():
            return result
        try:
            snippet, generator = self._exocoms_debrand_params()
            return debrand_html(result, snippet=snippet, generator=generator)
        except Exception:  # pragma: no cover - ne jamais casser un rendu
            _logger.exception("EXOCOMS debranding: échec du nettoyage du rendu QWeb")
            return result
