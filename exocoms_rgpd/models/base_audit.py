# -*- coding: utf-8 -*-
"""Hook générique de journalisation branché sur tous les modèles.

L'héritage du modèle abstrait ``base`` évite tout patch dynamique de méthode
et reste compatible avec les évolutions de l'ORM. Un garde-fou en tête de
chaque surcharge assure un coût négligeable pour les modèles non audités.
"""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# Modèles jamais audités : risque de récursion ou volumétrie ingérable.
NEVER_AUDIT = {
    "exocoms.rgpd.audit.log",
    "exocoms.rgpd.audit.rule",
    "ir.logging",
    "bus.bus",
    "bus.presence",
    "mail.tracking.value",
    "mail.notification",
}


class Base(models.AbstractModel):
    _inherit = "base"

    # ------------------------------------------------------------------
    def _rgpd_audit_config(self, action):
        """Retourne la configuration d'audit du modèle, ou None."""
        if self._name in NEVER_AUDIT or self._transient or self._abstract:
            return None
        if self.env.context.get("rgpd_skip_audit"):
            return None
        registry = self.env.registry
        if not getattr(registry, "ready", False):
            return None
        if "exocoms.rgpd.audit.rule" not in self.env:
            return None
        try:
            config = self.env["exocoms.rgpd.audit.rule"].sudo()._get_audited_models()
        except Exception:  # table absente pendant l'installation
            return None
        entry = config.get(self._name)
        if not entry or not entry.get(action):
            return None
        return entry

    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        config = records._rgpd_audit_config("create") if records else None
        if config:
            try:
                self.env["exocoms.rgpd.audit.log"].log_batch(
                    records, "create", list(vals_list), config
                )
            except Exception:  # pragma: no cover
                _logger.exception("RGPD: journalisation de création impossible")
        return records

    def write(self, vals):
        config = self._rgpd_audit_config("write")
        result = super().write(vals)
        if config and self:
            try:
                self.env["exocoms.rgpd.audit.log"].log_batch(self, "write", vals, config)
            except Exception:  # pragma: no cover
                _logger.exception("RGPD: journalisation de modification impossible")
        return result

    def unlink(self):
        config = self._rgpd_audit_config("unlink")
        snapshot = []
        if config and self:
            for record in self:
                snapshot.append(
                    {
                        "model": self._name,
                        "id": record.id,
                        "name": self.env["exocoms.rgpd.audit.log"]._safe_name(record),
                        "partner": self.env["exocoms.rgpd.audit.log"]._guess_partner(record),
                    }
                )
        result = super().unlink()
        if config and snapshot:
            try:
                Log = self.env["exocoms.rgpd.audit.log"].sudo()
                ip = Log._current_ip()
                Log.with_context(rgpd_skip_audit=True).create(
                    [
                        {
                            "action": "unlink",
                            "model_name": item["model"],
                            "model_label": self._description,
                            "res_id": item["id"],
                            "res_name": item["name"],
                            "partner_id": item["partner"],
                            "ip_address": ip,
                            "user_id": self.env.uid,
                        }
                        for item in snapshot
                    ]
                )
            except Exception:  # pragma: no cover
                _logger.exception("RGPD: journalisation de suppression impossible")
        return result

    def export_data(self, fields_to_export):
        config = self._rgpd_audit_config("export")
        result = super().export_data(fields_to_export)
        if config and self:
            try:
                self.env["exocoms.rgpd.audit.log"].log_batch(
                    self, "export",
                    {"fields": fields_to_export, "count": len(self)},
                    config,
                )
            except Exception:  # pragma: no cover
                _logger.exception("RGPD: journalisation d'export impossible")
        return result
