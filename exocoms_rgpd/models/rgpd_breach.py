# -*- coding: utf-8 -*-
"""Registre des violations de données - articles 33 et 34 du RGPD."""

import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class RgpdBreach(models.Model):
    _name = "exocoms.rgpd.breach"
    _description = "RGPD - Violation de données"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_discovery desc, id desc"

    name = fields.Char(
        string="Référence", required=True, copy=False, readonly=True,
        default=lambda self: _("Nouveau"), index=True,
    )
    title = fields.Char(string="Intitulé", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    state = fields.Selection(
        [
            ("draft", "Signalement"),
            ("analysis", "Analyse en cours"),
            ("contained", "Incident contenu"),
            ("notified", "Notifiée"),
            ("closed", "Clôturée"),
        ],
        string="État", default="draft", required=True, tracking=True,
    )
    active = fields.Boolean(default=True)

    # -- Chronologie -------------------------------------------------------
    date_incident = fields.Datetime(string="Date de l'incident", tracking=True)
    date_discovery = fields.Datetime(
        string="Date de découverte", required=True, default=fields.Datetime.now, tracking=True
    )
    date_deadline = fields.Datetime(
        string="Échéance de notification (72 h)", compute="_compute_deadline", store=True
    )
    hours_left = fields.Float(string="Heures restantes", compute="_compute_hours_left")
    is_late = fields.Boolean(compute="_compute_hours_left", string="Délai dépassé")
    date_containment = fields.Datetime(string="Date de confinement")

    # -- Nature -------------------------------------------------------------
    breach_nature = fields.Selection(
        [
            ("confidentiality", "Atteinte à la confidentialité (divulgation, accès non autorisé)"),
            ("integrity", "Atteinte à l'intégrité (altération)"),
            ("availability", "Atteinte à la disponibilité (perte, destruction)"),
            ("multiple", "Atteintes combinées"),
        ],
        string="Nature de la violation", required=True, default="confidentiality", tracking=True,
    )
    cause = fields.Selection(
        [
            ("external_attack", "Attaque externe (intrusion, rançongiciel, hameçonnage)"),
            ("internal_malicious", "Acte malveillant interne"),
            ("human_error", "Erreur humaine"),
            ("technical", "Défaillance technique"),
            ("loss_theft", "Perte ou vol de support"),
            ("processor", "Incident chez un sous-traitant"),
            ("other", "Autre"),
        ],
        string="Cause", required=True, default="human_error",
    )
    description = fields.Html(string="Description des faits", sanitize=True, required=True)
    treatment_ids = fields.Many2many("exocoms.rgpd.treatment", string="Traitements impactés")
    data_category_ids = fields.Many2many(
        "exocoms.rgpd.data.category", string="Catégories de données concernées"
    )
    subject_category_ids = fields.Many2many(
        "exocoms.rgpd.subject.category", string="Personnes concernées"
    )
    affected_persons = fields.Integer(string="Nombre de personnes concernées")
    affected_records = fields.Integer(string="Nombre d'enregistrements")
    is_estimate = fields.Boolean(string="Volumes estimés")

    # -- Risques -------------------------------------------------------------
    consequences = fields.Html(string="Conséquences probables", sanitize=True)
    risk_level = fields.Selection(
        [
            ("none", "Risque négligeable"),
            ("low", "Risque faible"),
            ("medium", "Risque"),
            ("high", "Risque élevé"),
        ],
        string="Niveau de risque", required=True, default="medium", tracking=True,
    )
    measures_taken = fields.Html(string="Mesures prises ou envisagées", sanitize=True)

    # -- Notifications ---------------------------------------------------------
    notify_authority = fields.Boolean(
        string="Notification à la CNIL requise", compute="_compute_notify", store=True,
        readonly=False, tracking=True,
    )
    authority_notified = fields.Boolean(string="CNIL notifiée", tracking=True)
    authority_date = fields.Datetime(string="Date de notification CNIL")
    authority_ref = fields.Char(string="Numéro d'accusé de réception")
    authority_delay_reason = fields.Text(string="Motif du retard (si > 72 h)")

    notify_subjects = fields.Boolean(
        string="Information des personnes requise", compute="_compute_notify", store=True,
        readonly=False, tracking=True,
    )
    subjects_notified = fields.Boolean(string="Personnes informées", tracking=True)
    subjects_date = fields.Datetime(string="Date d'information")
    subjects_method = fields.Char(string="Modalités d'information")
    subjects_exemption = fields.Selection(
        [
            ("encryption", "Données chiffrées et inintelligibles (art. 34.3.a)"),
            ("measures", "Mesures ultérieures écartant le risque (art. 34.3.b)"),
            ("effort", "Effort disproportionné : communication publique (art. 34.3.c)"),
        ],
        string="Exemption invoquée",
    )

    dpo_user_id = fields.Many2one(
        "res.users", string="DPO", default=lambda s: s.env.company.rgpd_dpo_user_id
    )
    responsible_user_id = fields.Many2one(
        "res.users", string="Responsable de l'incident", default=lambda s: s.env.user
    )
    lessons_learned = fields.Html(string="Retour d'expérience", sanitize=True)
    attachment_ids = fields.Many2many("ir.attachment", string="Pièces jointes")

    _rgpd_breach_name_uniq = models.Constraint(
        "unique(name, company_id)",
        "Cette référence de violation existe déjà.",
    )

    # ------------------------------------------------------------------
    @api.depends("date_discovery")
    def _compute_deadline(self):
        for rec in self:
            rec.date_deadline = (
                rec.date_discovery + relativedelta(hours=72) if rec.date_discovery else False
            )

    @api.depends("date_deadline", "authority_notified", "state")
    def _compute_hours_left(self):
        now = fields.Datetime.now()
        for rec in self:
            if not rec.date_deadline or rec.authority_notified or rec.state == "closed":
                rec.hours_left = 0.0
                rec.is_late = False
                continue
            delta = (rec.date_deadline - now).total_seconds() / 3600.0
            rec.hours_left = round(delta, 1)
            rec.is_late = delta < 0

    @api.depends("risk_level")
    def _compute_notify(self):
        for rec in self:
            rec.notify_authority = rec.risk_level != "none"
            rec.notify_subjects = rec.risk_level == "high"

    @api.depends("name", "title")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s - %s" % (rec.name, rec.title or "")

    @api.constrains("authority_notified", "authority_date", "date_deadline",
                    "authority_delay_reason")
    def _check_delay_justification(self):
        for rec in self:
            if (
                rec.authority_notified
                and rec.authority_date
                and rec.date_deadline
                and rec.authority_date > rec.date_deadline
                and not rec.authority_delay_reason
            ):
                raise ValidationError(
                    _("La notification est intervenue au-delà de 72 heures : "
                      "l'article 33.1 impose d'en indiquer le motif.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("Nouveau"):
                # with_company : si une séquence propre à la société existe,
                # elle est retenue ; sinon Odoo retombe sur la séquence
                # partagée (company_id vide).
                company_id = vals.get("company_id", self.env.company.id)
                vals["name"] = (
                    self.env["ir.sequence"]
                    .with_company(company_id)
                    .next_by_code("exocoms.rgpd.breach")
                ) or _("Nouveau")
        breaches = super().create(vals_list)
        breaches._alert_dpo()
        return breaches

    def _alert_dpo(self):
        for rec in self:
            if not rec.dpo_user_id:
                continue
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=fields.Date.context_today(rec),
                summary=_("Violation de données %s : qualifier et notifier sous 72 h") % rec.name,
                user_id=rec.dpo_user_id.id,
            )
            rec.message_post(
                body=_("Violation enregistrée. Échéance de notification à la CNIL : %s")
                % rec.date_deadline,
                partner_ids=rec.dpo_user_id.partner_id.ids,
            )

    # ------------------------------------------------------------------
    def action_analysis(self):
        self.write({"state": "analysis"})

    def action_contained(self):
        self.write({"state": "contained", "date_containment": fields.Datetime.now()})

    def action_notify_authority(self):
        for rec in self:
            rec.write(
                {
                    "authority_notified": True,
                    "authority_date": fields.Datetime.now(),
                    "state": "notified",
                }
            )
            rec.message_post(body=_("Notification à l'autorité de contrôle effectuée."))

    def action_notify_subjects(self):
        for rec in self:
            rec.write(
                {"subjects_notified": True, "subjects_date": fields.Datetime.now()}
            )
            rec.message_post(body=_("Personnes concernées informées."))

    def action_close(self):
        for rec in self:
            if rec.notify_authority and not rec.authority_notified:
                raise UserError(
                    _("La violation %s doit être notifiée à la CNIL, ou le "
                      "niveau de risque doit être requalifié, avant clôture.")
                    % rec.name
                )
            if rec.notify_subjects and not rec.subjects_notified and not rec.subjects_exemption:
                raise UserError(
                    _("Les personnes concernées doivent être informées, ou une "
                      "exemption de l'article 34.3 doit être invoquée.")
                )
            rec.state = "closed"

    def action_draft(self):
        self.write({"state": "draft"})

    @api.model
    def _cron_check_breach_deadline(self):
        now = fields.Datetime.now()
        # sudo : une violation non notifiée doit remonter quelle que soit la
        # société, l'échéance de 72 h ne dépend pas des droits du cron.
        pending = self.sudo().search(
            [("authority_notified", "=", False), ("notify_authority", "=", True),
             ("state", "!=", "closed")]
        )
        for rec in pending:
            if not rec.date_deadline:
                continue
            hours = (rec.date_deadline - now).total_seconds() / 3600.0
            if hours < 0:
                rec.message_post(
                    body=_("<b>Délai de 72 heures dépassé</b> pour la notification "
                           "à l'autorité de contrôle."),
                    subtype_xmlid="mail.mt_comment",
                )
            elif hours <= 12:
                rec.message_post(
                    body=_("Il reste moins de 12 heures pour notifier la CNIL.")
                )
        return True
