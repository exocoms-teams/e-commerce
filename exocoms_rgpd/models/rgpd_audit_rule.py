# -*- coding: utf-8 -*-
"""Configuration du journal d'audit par modèle."""

from odoo import _, api, fields, models, tools


class RgpdAuditRule(models.Model):
    _name = "exocoms.rgpd.audit.rule"
    _description = "RGPD - Règle de journalisation"
    _order = "model_name"

    name = fields.Char(string="Libellé", required=True)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        "ir.model", string="Modèle", required=True, ondelete="cascade",
        domain=[("transient", "=", False)],
    )
    model_name = fields.Char(related="model_id.model", store=True, index=True)
    log_create = fields.Boolean(string="Créations", default=True)
    log_write = fields.Boolean(string="Modifications", default=True)
    log_unlink = fields.Boolean(string="Suppressions", default=True)
    log_export = fields.Boolean(string="Exports", default=True)
    store_values = fields.Boolean(
        string="Conserver les valeurs", default=True,
        help="Enregistre les valeurs avant/après. À désactiver pour les modèles "
        "contenant des données sensibles afin de ne pas dupliquer celles-ci "
        "dans le journal.",
    )
    log_count = fields.Integer(compute="_compute_log_count", string="Entrées")
    note = fields.Text(string="Notes")

    _rgpd_audit_rule_model_uniq = models.Constraint(
        "unique(model_id)",
        "Une règle de journalisation existe déjà pour ce modèle.",
    )

    def _compute_log_count(self):
        Log = self.env["exocoms.rgpd.audit.log"]
        for rec in self:
            rec.log_count = Log.search_count([("model_name", "=", rec.model_name)])

    # ------------------------------------------------------------------
    # Cache utilisé par le hook générique sur ``base``
    # ------------------------------------------------------------------
    @tools.ormcache("self.env.company.id")
    def _get_audited_models(self):
        """Retourne {model_name: {'create': bool, 'write': bool, ...}}."""
        result = {}
        for rule in self.sudo().search([]):
            if not rule.model_name:
                continue
            result[rule.model_name] = {
                "create": rule.log_create,
                "write": rule.log_write,
                "unlink": rule.log_unlink,
                "export": rule.log_export,
                "values": rule.store_values,
            }
        return result

    def _clear_audit_cache(self):
        self.env.registry.clear_cache()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self._clear_audit_cache()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._clear_audit_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self._clear_audit_cache()
        return res

    def action_view_logs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Journal - %s") % self.name,
            "res_model": "exocoms.rgpd.audit.log",
            "view_mode": "list,form",
            "domain": [("model_name", "=", self.model_name)],
        }
