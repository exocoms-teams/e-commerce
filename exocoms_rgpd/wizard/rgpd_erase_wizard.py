# -*- coding: utf-8 -*-
"""Assistant d'effacement / anonymisation (art. 17)."""

import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RgpdEraseWizard(models.TransientModel):
    _name = "exocoms.rgpd.erase.wizard"
    _description = "RGPD - Assistant d'effacement des données"

    partner_id = fields.Many2one(
        "res.partner", string="Personne concernée", required=True
    )
    request_id = fields.Many2one("exocoms.rgpd.request", string="Demande liée")
    reason = fields.Text(string="Motif de l'effacement", required=True)
    confirm_text = fields.Char(
        string="Saisir ANONYMISER pour confirmer",
        help="Sécurité : l'opération est irréversible.",
    )
    simulation = fields.Text(string="Simulation", readonly=True)
    blocked = fields.Text(string="Données non effaçables", readonly=True)
    total_records = fields.Integer(string="Enregistrements impactés", readonly=True)
    state = fields.Selection(
        [("config", "Analyse"), ("done", "Terminé")], default="config"
    )
    result = fields.Text(string="Rapport", readonly=True)

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        partner_id = values.get("partner_id") or self.env.context.get("default_partner_id")
        if partner_id:
            values.update(self._simulate(self.env["res.partner"].browse(partner_id)))
        return values

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            for key, value in self._simulate(self.partner_id).items():
                self[key] = value

    def _simulate(self, partner):
        report = self.env["exocoms.rgpd.engine"].anonymize_partner(partner, dry_run=True)
        lines = [
            "%s : %s enregistrement(s) - champs %s"
            % (item["title"] or item["model"], item["count"], ", ".join(item["fields"]))
            for item in report["processed"]
        ]
        blocked = [
            "%s : %s enregistrement(s) conservés - %s"
            % (item["title"] or item["model"], item["count"], item["reason"])
            for item in report["blocked"]
        ]
        return {
            "simulation": "\n".join(lines) or _("Aucune donnée à anonymiser."),
            "blocked": "\n".join(blocked)
            or _("Aucune obligation légale de conservation identifiée."),
            "total_records": report["total"],
        }

    def action_erase(self):
        self.ensure_one()
        if (self.confirm_text or "").strip().upper() != "ANONYMISER":
            raise UserError(
                _("Saisissez exactement ANONYMISER pour confirmer l'opération.")
            )
        report = self.env["exocoms.rgpd.engine"].anonymize_partner(
            self.partner_id, dry_run=False, reason=self.reason
        )
        summary = json.dumps(report, indent=2, ensure_ascii=False, default=str)
        self.write({"state": "done", "result": summary})
        if self.request_id:
            self.request_id.write({"erasure_report": summary})
            self.request_id.message_post(
                body=_("Effacement exécuté : %s enregistrement(s) anonymisé(s). "
                       "Motif : %s") % (report["total"], self.reason)
            )
        self.partner_id.message_post(
            body=_("Données personnelles anonymisées au titre de l'article 17 du "
                   "RGPD. Motif : %s") % self.reason
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
