# -*- coding: utf-8 -*-
"""Journal d'audit des accès et modifications sur données personnelles."""

import json
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MAX_VALUE_LENGTH = 2000


class RgpdAuditLog(models.Model):
    _name = "exocoms.rgpd.audit.log"
    _description = "RGPD - Journal d'audit"
    _order = "date desc, id desc"
    _rec_name = "res_name"

    date = fields.Datetime(
        string="Horodatage", required=True, default=fields.Datetime.now, index=True
    )
    user_id = fields.Many2one(
        "res.users", string="Utilisateur", required=True, index=True,
        default=lambda self: self.env.user, ondelete="restrict",
    )
    action = fields.Selection(
        [
            ("create", "Création"),
            ("write", "Modification"),
            ("unlink", "Suppression"),
            ("export", "Export"),
            ("read", "Consultation"),
        ],
        string="Action", required=True, index=True,
    )
    model_name = fields.Char(string="Modèle", required=True, index=True)
    model_label = fields.Char(string="Libellé du modèle")
    res_id = fields.Integer(string="ID de l'enregistrement", index=True)
    res_name = fields.Char(string="Enregistrement")
    partner_id = fields.Many2one("res.partner", string="Personne concernée", index=True)
    values = fields.Text(string="Valeurs")
    field_names = fields.Char(string="Champs modifiés")
    ip_address = fields.Char(string="Adresse IP")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, index=True
    )

    def init(self):
        self.env.cr.execute(
            "CREATE INDEX IF NOT EXISTS exocoms_rgpd_audit_log_model_res_idx "
            "ON exocoms_rgpd_audit_log (model_name, res_id)"
        )

    # ------------------------------------------------------------------
    def write(self, vals):
        raise UserError(_("Le journal d'audit est en lecture seule."))

    def unlink(self):
        if not self.env.context.get("rgpd_purge_logs"):
            raise UserError(
                _("Les entrées du journal d'audit ne peuvent pas être supprimées "
                  "manuellement. Utilisez la purge automatique configurée dans "
                  "les paramètres.")
            )
        return super().unlink()

    # ------------------------------------------------------------------
    @api.model
    def log_batch(self, records, action, values=None, config=None):
        """Journalise une opération sur un recordset."""
        if not records:
            return
        config = config or {}
        model = records._name
        model_label = self.env["ir.model"]._get(model).name if model in self.env else model
        ip = self._current_ip()
        entries = []
        for index, record in enumerate(records):
            payload = False
            fnames = False
            if config.get("values", True) and values is not None:
                raw = values[index] if isinstance(values, list) and index < len(values) else values
                if isinstance(raw, dict):
                    fnames = ", ".join(sorted(raw.keys()))[:500]
                    try:
                        payload = json.dumps(raw, default=str, ensure_ascii=False)[:MAX_VALUE_LENGTH]
                    except Exception:
                        payload = str(raw)[:MAX_VALUE_LENGTH]
            entries.append(
                {
                    "action": action,
                    "model_name": model,
                    "model_label": model_label,
                    "res_id": record.id,
                    "res_name": self._safe_name(record),
                    "partner_id": self._guess_partner(record),
                    "values": payload,
                    "field_names": fnames,
                    "ip_address": ip,
                    "user_id": self.env.uid,
                }
            )
        if entries:
            self.sudo().with_context(rgpd_skip_audit=True).create(entries)

    @api.model
    def _safe_name(self, record):
        try:
            return (record.display_name or "")[:250]
        except Exception:
            return "#%s" % record.id

    @api.model
    def _guess_partner(self, record):
        for candidate in ("partner_id", "commercial_partner_id", "contact_id"):
            field = record._fields.get(candidate)
            if field is not None and field.type == "many2one" and field.comodel_name == "res.partner":
                try:
                    return record[candidate].id or False
                except Exception:
                    return False
        if record._name == "res.partner":
            return record.id
        return False

    @api.model
    def _current_ip(self):
        try:
            from odoo.http import request

            if request and request.httprequest:
                return request.httprequest.remote_addr
        except Exception:
            pass
        return False

    # ------------------------------------------------------------------
    @api.model
    def _cron_purge_logs(self):
        months = int(
            self.env["ir.config_parameter"].sudo().get_param(
                "exocoms_rgpd.audit_retention_months", "12"
            )
        )
        if months <= 0:
            return True
        cutoff = fields.Datetime.now() - relativedelta(months=months)
        # sudo : la purge s'applique à toutes les sociétés.
        old = self.sudo().search([("date", "<", cutoff)], limit=20000)
        count = len(old)
        if old:
            old.with_context(rgpd_purge_logs=True).unlink()
        _logger.info("RGPD: %s entrée(s) de journal purgée(s).", count)
        return True

    def action_open_record(self):
        self.ensure_one()
        if not self.res_id or self.model_name not in self.env:
            raise UserError(_("L'enregistrement d'origine n'existe plus."))
        return {
            "type": "ir.actions.act_window",
            "res_model": self.model_name,
            "res_id": self.res_id,
            "view_mode": "form",
        }
