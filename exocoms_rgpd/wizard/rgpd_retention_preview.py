# -*- coding: utf-8 -*-
"""Simulation avant application d'une règle de conservation."""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RgpdRetentionPreview(models.TransientModel):
    _name = "exocoms.rgpd.retention.preview"
    _description = "RGPD - Simulation de la politique de conservation"

    rule_id = fields.Many2one(
        "exocoms.rgpd.retention.rule", string="Règle", required=True
    )
    model_name = fields.Char(related="rule_id.model_name", readonly=True)
    action_type = fields.Selection(related="rule_id.action_type", readonly=True)
    cutoff_date = fields.Datetime(string="Antérieur au", readonly=True)
    match_count = fields.Integer(string="Enregistrements concernés", readonly=True)
    batch_size = fields.Integer(related="rule_id.batch_size", readonly=True)
    sample = fields.Text(string="Échantillon", readonly=True)
    warning = fields.Text(string="Avertissement", readonly=True)
    confirm_text = fields.Char(string="Saisir APPLIQUER pour confirmer")

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        rule_id = values.get("rule_id") or self.env.context.get("default_rule_id")
        if not rule_id:
            return values
        rule = self.env["exocoms.rgpd.retention.rule"].browse(rule_id)
        model = self.env.get(rule.model_name)
        if model is None:
            raise UserError(_("Le modèle %s n'est pas installé.") % rule.model_name)
        domain = rule._build_domain()
        count = model.sudo().with_context(active_test=False).search_count(domain)
        sample_records = model.sudo().with_context(active_test=False).search(domain, limit=15)
        values.update(
            {
                "cutoff_date": rule._cutoff_date(),
                "match_count": count,
                "sample": "\n".join(
                    "#%s - %s" % (rec.id, rec.display_name) for rec in sample_records
                ) or _("Aucun enregistrement."),
            }
        )
        if rule.action_type == "delete":
            values["warning"] = _(
                "ATTENTION : cette règle supprime définitivement les "
                "enregistrements. L'opération est irréversible et peut rompre "
                "des liens avec d'autres documents. Vérifiez qu'aucune "
                "obligation légale de conservation ne s'applique."
            )
        elif rule.action_type == "anonymize":
            values["warning"] = _(
                "L'anonymisation est irréversible. Les données ne pourront plus "
                "être reconstituées."
            )
        return values

    def action_apply(self):
        self.ensure_one()
        if (self.confirm_text or "").strip().upper() != "APPLIQUER":
            raise UserError(_("Saisissez exactement APPLIQUER pour confirmer."))
        count = self.rule_id.action_run(force=True)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Règle appliquée"),
                "message": _("%s enregistrement(s) traité(s).") % count,
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
