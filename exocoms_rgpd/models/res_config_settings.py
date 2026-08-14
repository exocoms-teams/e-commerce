# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rgpd_dpo_user_id = fields.Many2one(
        related="company_id.rgpd_dpo_user_id", readonly=False,
        string="Délégué à la protection des données",
    )
    rgpd_dpo_name = fields.Char(related="company_id.rgpd_dpo_name", readonly=False)
    rgpd_dpo_email = fields.Char(related="company_id.rgpd_dpo_email", readonly=False)
    rgpd_dpo_phone = fields.Char(related="company_id.rgpd_dpo_phone", readonly=False)
    rgpd_dpo_address = fields.Text(related="company_id.rgpd_dpo_address", readonly=False)
    rgpd_authority_name = fields.Char(related="company_id.rgpd_authority_name", readonly=False)
    rgpd_authority_url = fields.Char(related="company_id.rgpd_authority_url", readonly=False)
    rgpd_portal_enabled = fields.Boolean(related="company_id.rgpd_portal_enabled", readonly=False)
    rgpd_public_form_enabled = fields.Boolean(
        related="company_id.rgpd_public_form_enabled", readonly=False
    )
    rgpd_auto_acknowledge = fields.Boolean(
        related="company_id.rgpd_auto_acknowledge", readonly=False
    )
    rgpd_privacy_policy_url = fields.Char(
        related="company_id.rgpd_privacy_policy_url", readonly=False
    )
    rgpd_blacklist_sync = fields.Boolean(
        related="company_id.rgpd_blacklist_sync", readonly=False
    )

    rgpd_audit_retention_months = fields.Integer(
        string="Conservation du journal d'audit (mois)",
        config_parameter="exocoms_rgpd.audit_retention_months",
        default=12,
    )
    rgpd_hash_salt = fields.Char(
        string="Sel de pseudonymisation",
        config_parameter="exocoms_rgpd.hash_salt",
        help="Chaîne secrète utilisée pour le hachage SHA-256. Ne la modifiez "
        "plus une fois des données pseudonymisées : les empreintes ne seraient "
        "plus comparables.",
    )
    rgpd_consent_api_key = fields.Char(
        string="Clé d'API consentements",
        config_parameter="exocoms_rgpd.consent_api_key",
        help="Clé attendue dans l'en-tête X-RGPD-Key par l'endpoint "
        "/rgpd/consent/log utilisé par les CMP externes.",
    )

    rgpd_own_sequences = fields.Boolean(
        string="Numérotation propre à cette société",
        compute="_compute_rgpd_own_sequences",
        help="Par défaut les références RGPD/, TRT/ et VIOL/ sont continues sur "
        "l'ensemble des sociétés. Générez des séquences dédiées pour que cette "
        "entité numérote indépendamment des autres.",
    )

    @api.depends("company_id")
    def _compute_rgpd_own_sequences(self):
        for rec in self:
            rec.rgpd_own_sequences = (
                rec.company_id._rgpd_has_own_sequences() if rec.company_id else False
            )

    def action_create_rgpd_sequences(self):
        """Dote la société courante de ses propres séquences RGPD.

        Les compteurs repartent de 1 : les références déjà attribuées ne sont
        pas renumérotées, elles restent valides et référencées dans les
        échanges avec les personnes concernées.
        """
        self.ensure_one()
        created = self.company_id._rgpd_create_sequences()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Séquences créées"),
                "message": _(
                    "%s séquence(s) propre(s) à %s. Les nouvelles références "
                    "repartent de 1 ; les références déjà attribuées restent "
                    "inchangées."
                ) % (len(created), self.company_id.name),
                "type": "success" if created else "warning",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    def action_reconcile_blacklist(self):
        """Réaligne la liste noire sur le journal des consentements."""
        self.ensure_one()
        Reconcile = self.env["exocoms.rgpd.consent"]
        divergences = Reconcile._divergences()
        Reconcile._cron_reconcile_blacklist()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Réconciliation terminée"),
                "message": _("%s divergence(s) corrigée(s) entre le journal des "
                             "consentements et la liste noire de messagerie.")
                % len(divergences),
                "type": "success" if divergences else "info",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    def action_open_data_map(self):
        return self.env.ref("exocoms_rgpd.action_rgpd_data_map").read()[0]

    def action_autodetect_data_map(self):
        return self.env["exocoms.rgpd.data.map"].action_autodetect()
