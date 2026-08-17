# -*- coding: utf-8 -*-
"""Politique de conservation : purge, anonymisation et archivage automatiques."""

import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from .rgpd_engine import STRATEGIES

_logger = logging.getLogger(__name__)


class RgpdRetentionRule(models.Model):
    _name = "exocoms.rgpd.retention.rule"
    _description = "RGPD - Règle de conservation"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    name = fields.Char(string="Règle", required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, index=True
    )
    treatment_id = fields.Many2one(
        "exocoms.rgpd.treatment", string="Traitement lié", ondelete="set null"
    )
    model_id = fields.Many2one(
        "ir.model", string="Modèle", required=True, ondelete="cascade",
        domain=[("transient", "=", False)],
    )
    model_name = fields.Char(related="model_id.model", store=True)
    date_field_id = fields.Many2one(
        "ir.model.fields", string="Champ de référence", required=True, ondelete="cascade",
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['date', 'datetime'])]",
        help="Champ servant de point de départ au calcul de la durée "
        "(date de dernière activité, date de clôture, date de création...).",
    )
    date_field_name = fields.Char(related="date_field_id.name", store=True)
    domain = fields.Char(
        string="Filtre complémentaire", default="[]",
        help="Restreint les enregistrements concernés, ex. [('state','=','done')]",
    )

    retention_value = fields.Integer(string="Durée", required=True, default=3)
    retention_unit = fields.Selection(
        [("day", "Jour(s)"), ("month", "Mois"), ("year", "An(s)")],
        string="Unité", required=True, default="year",
    )
    action_type = fields.Selection(
        [
            ("anonymize", "Anonymiser les champs listés"),
            ("archive", "Archiver (active = False)"),
            ("delete", "Supprimer définitivement"),
        ],
        string="Action", required=True, default="anonymize", tracking=True,
    )
    field_ids = fields.One2many(
        "exocoms.rgpd.retention.field", "rule_id", string="Champs à anonymiser"
    )
    batch_size = fields.Integer(
        string="Lot par exécution", default=500,
        help="Nombre maximal d'enregistrements traités à chaque passage du cron.",
    )
    auto_run = fields.Boolean(string="Exécution automatique", default=False, tracking=True)
    require_confirmation = fields.Boolean(
        string="Confirmation manuelle requise", default=True,
        help="Décochez uniquement après avoir validé la simulation.",
    )

    last_run = fields.Datetime(string="Dernière exécution", readonly=True)
    last_count = fields.Integer(string="Enregistrements traités", readonly=True)
    total_processed = fields.Integer(string="Total cumulé", readonly=True)
    pending_count = fields.Integer(string="En attente", compute="_compute_pending_count")
    legal_basis_note = fields.Text(
        string="Justification de la durée",
        help="Référence au texte imposant ou justifiant la durée retenue "
        "(art. L123-22 du Code de commerce, prescription triennale...).",
    )

    @api.constrains("action_type", "field_ids")
    def _check_fields(self):
        for rec in self:
            if rec.action_type == "anonymize" and not rec.field_ids:
                raise ValidationError(
                    _("Une règle d'anonymisation doit lister au moins un champ.")
                )

    @api.constrains("retention_value")
    def _check_value(self):
        for rec in self:
            if rec.retention_value <= 0:
                raise ValidationError(_("La durée de conservation doit être positive."))

    @api.constrains("action_type", "auto_run", "require_confirmation")
    def _check_delete_safety(self):
        for rec in self:
            if rec.action_type == "delete" and rec.auto_run and rec.require_confirmation:
                raise ValidationError(
                    _("Une règle de suppression automatique ne peut pas exiger "
                      "en même temps une confirmation manuelle. Décochez l'une "
                      "des deux options en connaissance de cause.")
                )

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.date_field_id = False
        self.field_ids = [(5, 0, 0)]
        if not self.model_id:
            return
        preferred = ("write_date", "date_closed", "date_end", "create_date")
        for candidate in preferred:
            field = self.env["ir.model.fields"].search(
                [("model", "=", self.model_id.model), ("name", "=", candidate)], limit=1
            )
            if field:
                self.date_field_id = field
                break

    # ------------------------------------------------------------------
    def _cutoff_date(self):
        self.ensure_one()
        delta = {
            "day": relativedelta(days=self.retention_value),
            "month": relativedelta(months=self.retention_value),
            "year": relativedelta(years=self.retention_value),
        }[self.retention_unit]
        return fields.Datetime.now() - delta

    def _company_domain(self):
        """Restreint la règle aux enregistrements de sa propre société.

        Sans ce filtre, une règle définie pour la société A anonymiserait ou
        supprimerait aussi les enregistrements de la société B : en
        multi-société c'est une perte de données irréversible. Le filtre n'est
        appliqué que si le modèle cible porte réellement un ``company_id``.
        Les enregistrements sans société (partagés) sont inclus uniquement
        lorsque la règle est elle-même partagée.
        """
        self.ensure_one()
        model = self.env.get(self.model_name)
        if model is None or "company_id" not in model._fields:
            return []
        if not self.company_id:
            # Règle partagée : elle couvre l'ensemble des sociétés.
            return []
        return ["|", ("company_id", "=", False), ("company_id", "=", self.company_id.id)]

    def _build_domain(self):
        self.ensure_one()
        domain = [(self.date_field_name, "<", fields.Datetime.to_string(self._cutoff_date()))]
        domain += self._company_domain()
        if self.domain:
            domain += safe_eval(self.domain)
        if self.action_type == "archive":
            model = self.env.get(self.model_name)
            if model is not None and "active" in model._fields:
                domain += [("active", "=", True)]
        return domain

    def _get_expired_records(self, limit=None):
        self.ensure_one()
        model = self.env.get(self.model_name)
        if model is None:
            return None
        return (
            model.sudo()
            .with_context(active_test=False)
            .search(self._build_domain(), limit=limit or self.batch_size, order="id")
        )

    def _compute_pending_count(self):
        for rec in self:
            model = self.env.get(rec.model_name)
            if model is None or not rec.date_field_name:
                rec.pending_count = 0
                continue
            try:
                rec.pending_count = model.sudo().with_context(
                    active_test=False
                ).search_count(rec._build_domain())
            except Exception:
                rec.pending_count = 0

    # ------------------------------------------------------------------
    def action_preview(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Simulation - %s") % self.name,
            "res_model": "exocoms.rgpd.retention.preview",
            "view_mode": "form",
            "target": "new",
            "context": {"default_rule_id": self.id},
        }

    def action_open_records(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Enregistrements concernés"),
            "res_model": self.model_name,
            "view_mode": "list,form",
            "domain": self._build_domain(),
            "context": {"active_test": False},
        }

    def action_run(self, force=False):
        """Applique la règle. Retourne le nombre d'enregistrements traités."""
        total = 0
        for rec in self:
            if rec.require_confirmation and not force:
                raise UserError(
                    _("La règle « %s » exige une confirmation manuelle. Lancez-la "
                      "depuis la simulation ou décochez l'option.") % rec.name
                )
            records = rec._get_expired_records()
            if records is None:
                _logger.warning("RGPD: modèle %s introuvable.", rec.model_name)
                continue
            count = 0
            if records:
                if rec.action_type == "anonymize":
                    count = self.env["exocoms.rgpd.engine"].anonymize_records(
                        records, rec.field_ids, dry_run=False
                    )
                elif rec.action_type == "archive":
                    model = self.env[rec.model_name]
                    if "active" not in model._fields:
                        raise UserError(
                            _("Le modèle %s ne gère pas l'archivage.") % rec.model_name
                        )
                    records.with_context(rgpd_anonymizing=True,mail_notrack=True).write({"active": False})
                    count = len(records)
                elif rec.action_type == "delete":
                    count = len(records)
                    records.with_context(rgpd_anonymizing=True).unlink()
            rec.write(
                {
                    "last_run": fields.Datetime.now(),
                    "last_count": count,
                    "total_processed": rec.total_processed + count,
                }
            )
            if count:
                rec.message_post(
                    body=_("%(count)s enregistrement(s) traité(s) (%(action)s) sur %(model)s.")
                    % {
                        "count": count,
                        "action": dict(
                            self._fields["action_type"]._description_selection(self.env)
                        ).get(rec.action_type),
                        "model": rec.model_name,
                    }
                )
            total += count
        return total

    def action_run_manual(self):
        count = self.action_run(force=True)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Politique de conservation appliquée"),
                "message": _("%s enregistrement(s) traité(s).") % count,
                "type": "success",
            },
        }

    @api.model
    def _cron_apply_retention(self):
        # sudo : les règles de toutes les sociétés doivent s'exécuter.
        # Chaque règle reste cloisonnée sur sa propre société par
        # ``_company_domain()``.
        rules = self.sudo().search([("auto_run", "=", True)])
        total = 0
        for rule in rules:
            try:
                total += rule.action_run(force=True)
                self.env.cr.commit()
            except Exception:  # pragma: no cover
                self.env.cr.rollback()
                _logger.exception("RGPD: échec de la règle de conservation %s", rule.name)
        _logger.info("RGPD: conservation appliquée sur %s enregistrement(s).", total)
        return True


class RgpdRetentionField(models.Model):
    _name = "exocoms.rgpd.retention.field"
    _description = "RGPD - Champ soumis à anonymisation"
    _order = "rule_id, sequence, id"

    rule_id = fields.Many2one(
        "exocoms.rgpd.retention.rule", string="Règle", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    model_name = fields.Char(related="rule_id.model_name", store=True)
    field_id = fields.Many2one(
        "ir.model.fields", string="Champ", required=True, ondelete="cascade",
        domain="[('model', '=', model_name)]",
    )
    field_name = fields.Char(related="field_id.name", store=True)
    strategy = fields.Selection(
        STRATEGIES, string="Stratégie", required=True, default="clear"
    )
    fixed_value = fields.Char(string="Valeur fixe")

    _rgpd_retention_field_uniq = models.Constraint(
        "unique(rule_id, field_id)",
        "Ce champ figure déjà dans la règle.",
    )
