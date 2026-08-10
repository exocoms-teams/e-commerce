# -*- coding: utf-8 -*-
import logging

from markupsafe import Markup

from odoo import models

from ..tools.debrand import debrand_html

_logger = logging.getLogger(__name__)

FALSY = ("False", "false", "0", "", "None")


class MailRenderMixin(models.AbstractModel):
    """Filet de sécurité pour les corps de mail rendus hors QWeb.

    Les templates ``inline_template`` passent par ici : on nettoie le résultat
    au cas où une mention Odoo aurait été stockée en dur dans un template.
    """

    _inherit = "mail.render.mixin"

    def _exocoms_debrand_enabled(self):
        if self.env.context.get("exocoms_skip_debrand"):
            return False
        try:
            value = self.env["ir.config_parameter"].sudo().get_param(
                "exocoms_debranding.enabled", "True"
            )
        except Exception:  # pragma: no cover
            return False
        return value not in FALSY

    def _render_template(self, *args, **kwargs):
        result = super()._render_template(*args, **kwargs)
        if not isinstance(result, dict) or not self._exocoms_debrand_enabled():
            return result
        company = self.env.company
        snippet = company._debrand_snippet() if company else None
        generator = company._debrand_name() if company else None
        try:
            for res_id, value in result.items():
                if isinstance(value, str):
                    cleaned = debrand_html(value, snippet=snippet, generator=generator)
                    if cleaned is not value:
                        result[res_id] = (
                            Markup(cleaned) if isinstance(value, Markup) else cleaned
                        )
        except Exception:  # pragma: no cover
            _logger.exception("EXOCOMS debranding: échec du nettoyage d'un template mail")
        return result
