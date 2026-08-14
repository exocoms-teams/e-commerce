# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    rgpd_anonymized = fields.Boolean(
        string="Données anonymisées", readonly=True, copy=False
    )
    rgpd_anonymized_date = fields.Datetime(
        string="Date d'anonymisation", readonly=True, copy=False
    )
    rgpd_request_ids = fields.One2many(
        "exocoms.rgpd.request", "partner_id", string="Demandes RGPD"
    )
    rgpd_request_count = fields.Integer(compute="_compute_rgpd_counts")
    rgpd_consent_ids = fields.One2many(
        "exocoms.rgpd.consent", "partner_id", string="Consentements"
    )
    rgpd_consent_count = fields.Integer(compute="_compute_rgpd_counts")
    rgpd_marketing_ok = fields.Boolean(
        string="Consentement marketing", compute="_compute_rgpd_marketing_ok",
        search="_search_rgpd_marketing_ok",
    )

    def _compute_rgpd_counts(self):
        Request = self.env["exocoms.rgpd.request"]
        Consent = self.env["exocoms.rgpd.consent"]
        for partner in self:
            partner.rgpd_request_count = Request.search_count(
                [("partner_id", "=", partner.id)]
            )
            partner.rgpd_consent_count = Consent.search_count(
                [("partner_id", "=", partner.id)]
            )

    def _compute_rgpd_marketing_ok(self):
        Consent = self.env["exocoms.rgpd.consent"]
        for partner in self:
            current = Consent.sudo().get_current_state(partner.email, partner)
            partner.rgpd_marketing_ok = any(
                consent.state == "granted"
                and consent.purpose_id.category == "marketing"
                for consent in current.values()
            )

    def _search_rgpd_marketing_ok(self, operator, value):
        Consent = self.env["exocoms.rgpd.consent"].sudo()
        granted = Consent.search(
            [("state", "=", "granted"), ("purpose_id.category", "=", "marketing")]
        ).mapped("partner_id").ids
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("id", "in", granted)]
        return [("id", "not in", granted)]

    # ------------------------------------------------------------------
    def action_view_rgpd_requests(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Demandes RGPD"),
            "res_model": "exocoms.rgpd.request",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {
                "default_partner_id": self.id,
                "default_requester_name": self.name,
                "default_email": self.email,
            },
        }

    def action_view_rgpd_consents(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Consentements"),
            "res_model": "exocoms.rgpd.consent",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id, "default_email": self.email},
        }

    def action_rgpd_export(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Export des données personnelles"),
            "res_model": "exocoms.rgpd.export.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_partner_id": self.id},
        }

    def action_rgpd_erase(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Effacement des données personnelles"),
            "res_model": "exocoms.rgpd.erase.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_partner_id": self.id},
        }
