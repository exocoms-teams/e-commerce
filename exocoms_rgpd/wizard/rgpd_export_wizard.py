# -*- coding: utf-8 -*-
"""Assistant d'export des données personnelles (art. 15 et 20)."""

import base64
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RgpdExportWizard(models.TransientModel):
    _name = "exocoms.rgpd.export.wizard"
    _description = "RGPD - Assistant d'export des données personnelles"

    partner_id = fields.Many2one(
        "res.partner", string="Personne concernée", required=True
    )
    request_id = fields.Many2one("exocoms.rgpd.request", string="Demande liée")
    export_format = fields.Selection(
        [("json", "JSON (portabilité)"), ("pdf", "PDF (droit d'accès)"), ("both", "Les deux")],
        string="Format", default="both", required=True,
    )
    preview = fields.Text(string="Aperçu", readonly=True)
    section_count = fields.Integer(string="Sections", readonly=True)
    record_count = fields.Integer(string="Enregistrements", readonly=True)
    file_data = fields.Binary(string="Fichier", readonly=True, attachment=False)
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    state = fields.Selection(
        [("config", "Configuration"), ("done", "Terminé")], default="config"
    )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if not self.partner_id:
            self.preview = False
            return
        data = self.env["exocoms.rgpd.engine"].collect_personal_data(self.partner_id)
        self.section_count = len(data["sections"])
        self.record_count = sum(section["count"] for section in data["sections"])
        lines = [
            "%s : %s enregistrement(s)" % (section["title"], section["count"])
            for section in data["sections"]
        ]
        self.preview = "\n".join(lines) or _("Aucune donnée personnelle trouvée.")

    def action_generate(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Sélectionnez une personne."))
        data = self.env["exocoms.rgpd.engine"].collect_personal_data(self.partner_id)
        payload = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        slug = (self.partner_id.name or "contact").replace(" ", "-").lower()[:40]
        self.write(
            {
                "file_data": base64.b64encode(payload.encode("utf-8")),
                "file_name": "donnees-personnelles-%s.json" % slug,
                "state": "done",
                "section_count": len(data["sections"]),
                "record_count": sum(section["count"] for section in data["sections"]),
            }
        )
        if self.request_id:
            self.request_id.write(
                {
                    "export_data": self.file_data,
                    "export_filename": self.file_name,
                }
            )
            self.request_id.message_post(
                body=_("Export des données généré depuis l'assistant.")
            )
        if self.export_format == "pdf":
            return self.action_print_pdf()
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref(
            "exocoms_rgpd.action_report_rgpd_partner_export"
        ).report_action(self.partner_id)
