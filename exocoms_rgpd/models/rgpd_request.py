# -*- coding: utf-8 -*-
"""Demandes d'exercice des droits - articles 15 à 22 du RGPD."""

import base64
import json
import logging
import secrets

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

REQUEST_TYPES = [
    ("access", "Droit d'accès (art. 15)"),
    ("portability", "Droit à la portabilité (art. 20)"),
    ("rectification", "Droit de rectification (art. 16)"),
    ("erasure", "Droit à l'effacement (art. 17)"),
    ("restriction", "Droit à la limitation (art. 18)"),
    ("objection", "Droit d'opposition (art. 21)"),
    ("automated", "Décision automatisée (art. 22)"),
    ("withdraw", "Retrait du consentement (art. 7.3)"),
    ("info", "Demande d'information"),
]


class RgpdRequest(models.Model):
    _name = "exocoms.rgpd.request"
    _description = "RGPD - Demande d'exercice des droits"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_deadline asc, id desc"

    name = fields.Char(
        string="Référence", required=True, copy=False, readonly=True,
        default=lambda self: _("Nouveau"), index=True,
    )
    request_type = fields.Selection(
        REQUEST_TYPES, string="Nature de la demande", required=True,
        default="access", tracking=True,
    )
    state = fields.Selection(
        [
            ("new", "Reçue"),
            ("identity", "Vérification d'identité"),
            ("progress", "En traitement"),
            ("extended", "Délai prorogé"),
            ("done", "Clôturée"),
            ("refused", "Refusée"),
            ("cancel", "Annulée"),
        ],
        string="État", default="new", required=True, tracking=True, index=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True, index=True
    )

    # -- Demandeur --------------------------------------------------------
    partner_id = fields.Many2one(
        "res.partner", string="Personne concernée", tracking=True, index=True
    )
    requester_name = fields.Char(string="Nom du demandeur", required=True, tracking=True)
    email = fields.Char(string="E-mail", required=True, tracking=True, index=True)
    phone = fields.Char(string="Téléphone")
    is_third_party = fields.Boolean(
        string="Demande faite par un tiers",
        help="Représentant légal, mandataire, héritier. Une pièce justificative "
        "du mandat est requise.",
    )
    source = fields.Selection(
        [
            ("portal", "Portail client"),
            ("public_form", "Formulaire public"),
            ("email", "E-mail"),
            ("mail", "Courrier postal"),
            ("phone", "Téléphone"),
            ("onsite", "Sur place"),
            ("other", "Autre"),
        ],
        string="Canal de réception", default="email", required=True,
    )

    # -- Contenu ----------------------------------------------------------
    description = fields.Text(string="Demande exprimée")
    scope_note = fields.Text(string="Périmètre retenu")
    user_id = fields.Many2one(
        "res.users", string="Responsable du traitement de la demande", tracking=True,
        default=lambda self: self.env.company.rgpd_dpo_user_id or self.env.user,
    )

    # -- Identité ---------------------------------------------------------
    identity_verified = fields.Boolean(string="Identité vérifiée", tracking=True)
    identity_date = fields.Datetime(string="Date de vérification", readonly=True)
    identity_method = fields.Selection(
        [
            ("portal", "Authentification portail"),
            ("email_token", "Jeton envoyé par e-mail"),
            ("id_document", "Pièce d'identité"),
            ("known", "Personne connue du service"),
            ("other", "Autre"),
        ],
        string="Moyen de vérification",
    )
    identity_note = fields.Char(string="Précisions sur la vérification")
    access_token = fields.Char(string="Jeton de vérification", copy=False, groups="exocoms_rgpd.group_rgpd_officer")

    # -- Délais -----------------------------------------------------------
    date_request = fields.Datetime(
        string="Date de réception", required=True, default=fields.Datetime.now, tracking=True
    )
    date_deadline = fields.Date(
        string="Échéance légale", compute="_compute_deadline", store=True, tracking=True
    )
    extension_granted = fields.Boolean(string="Prorogation appliquée", tracking=True)
    extension_reason = fields.Text(string="Motif de la prorogation")
    date_response = fields.Datetime(string="Date de réponse", readonly=True, tracking=True)
    days_left = fields.Integer(string="Jours restants", compute="_compute_days_left")
    is_late = fields.Boolean(string="En retard", compute="_compute_days_left", search="_search_is_late")
    color = fields.Integer(compute="_compute_days_left")

    # -- Réponse ----------------------------------------------------------
    response_note = fields.Html(string="Réponse apportée", sanitize=True)
    refusal_ground = fields.Selection(
        [
            ("unfounded", "Demande manifestement infondée"),
            ("excessive", "Demande excessive (répétitive)"),
            ("identity", "Identité non établie"),
            ("legal", "Obligation légale de conservation"),
            ("rights", "Atteinte aux droits de tiers"),
            ("no_data", "Aucune donnée détenue"),
            ("other", "Autre motif"),
        ],
        string="Motif de refus", tracking=True,
    )
    refusal_note = fields.Text(string="Détail du refus")
    attachment_ids = fields.Many2many(
        "ir.attachment", string="Pièces jointes",
        relation="rgpd_request_attachment_rel", column1="request_id", column2="attachment_id",
    )
    export_data = fields.Binary(string="Export JSON", attachment=True, readonly=True)
    export_filename = fields.Char(string="Nom du fichier", readonly=True)
    erasure_report = fields.Text(string="Rapport d'effacement", readonly=True)
    treatment_ids = fields.Many2many("exocoms.rgpd.treatment", string="Traitements concernés")

    _rgpd_request_name_uniq = models.Constraint(
        "unique(name, company_id)",
        "Cette référence de demande existe déjà.",
    )

    # ------------------------------------------------------------------
    # Calculs
    # ------------------------------------------------------------------
    @api.depends("date_request", "extension_granted")
    def _compute_deadline(self):
        for rec in self:
            if not rec.date_request:
                rec.date_deadline = False
                continue
            base = fields.Datetime.to_datetime(rec.date_request).date()
            months = 3 if rec.extension_granted else 1
            rec.date_deadline = base + relativedelta(months=months)

    @api.depends("date_deadline", "state")
    def _compute_days_left(self):
        today = fields.Date.context_today(self)
        for rec in self:
            closed = rec.state in ("done", "refused", "cancel")
            if not rec.date_deadline or closed:
                rec.days_left = 0
                rec.is_late = False
                rec.color = 10 if rec.state == "done" else 0
                continue
            delta = (rec.date_deadline - today).days
            rec.days_left = delta
            rec.is_late = delta < 0
            rec.color = 1 if delta < 0 else (3 if delta <= 7 else 0)

    def _search_is_late(self, operator, value):
        today = fields.Date.context_today(self)
        late = [("date_deadline", "<", today),
                ("state", "not in", ["done", "refused", "cancel"])]
        if (operator == "=" and value) or (operator == "!=" and not value):
            return late
        return ["|", ("date_deadline", ">=", today),
                ("state", "in", ["done", "refused", "cancel"])]

    @api.depends("name", "requester_name", "request_type")
    def _compute_display_name(self):
        labels = dict(self._fields["request_type"]._description_selection(self.env))
        for rec in self:
            rec.display_name = "%s - %s (%s)" % (
                rec.name, rec.requester_name or "", labels.get(rec.request_type, "")
            )

    # ------------------------------------------------------------------
    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.requester_name = self.partner_id.name
            self.email = self.partner_id.email
            self.phone = self.partner_id.phone

    @api.constrains("state", "identity_verified")
    def _check_identity_before_close(self):
        for rec in self:
            if rec.state == "done" and not rec.identity_verified:
                raise ValidationError(
                    _("Impossible de clôturer la demande %s : l'identité du "
                      "demandeur n'a pas été vérifiée. Répondre à une personne "
                      "non identifiée constitue une violation de données.")
                    % rec.name
                )

    # ------------------------------------------------------------------
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
                    .next_by_code("exocoms.rgpd.request")
                ) or _("Nouveau")
            if not vals.get("access_token"):
                vals["access_token"] = secrets.token_urlsafe(32)
            if not vals.get("partner_id") and vals.get("email"):
                partner = self.env["res.partner"].sudo().search(
                    [("email", "=ilike", vals["email"])], limit=1
                )
                if partner:
                    vals["partner_id"] = partner.id
        requests = super().create(vals_list)
        for req in requests:
            req._schedule_activity()
            if req.company_id.rgpd_auto_acknowledge:
                req._send_acknowledgement()
        return requests

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------
    def _schedule_activity(self):
        for rec in self:
            if not rec.user_id or not rec.date_deadline:
                continue
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=rec.date_deadline - relativedelta(days=5),
                summary=_("Répondre à la demande RGPD %s") % rec.name,
                user_id=rec.user_id.id,
            )

    def _send_acknowledgement(self):
        template = self.env.ref(
            "exocoms_rgpd.mail_template_rgpd_request_ack", raise_if_not_found=False
        )
        for rec in self:
            if template and rec.email:
                template.send_mail(rec.id, force_send=False)

    def action_send_identity_check(self):
        template = self.env.ref(
            "exocoms_rgpd.mail_template_rgpd_identity_check", raise_if_not_found=False
        )
        for rec in self:
            rec.state = "identity"
            if template and rec.email:
                template.send_mail(rec.id, force_send=True)
        return True

    def action_confirm_identity(self):
        self.write(
            {
                "identity_verified": True,
                "identity_date": fields.Datetime.now(),
                "state": "progress",
            }
        )
        for rec in self.filtered(lambda r: not r.identity_method):
            rec.identity_method = "id_document"
        return True

    def action_start(self):
        for rec in self:
            if not rec.identity_verified:
                raise UserError(
                    _("Vérifiez d'abord l'identité du demandeur avant d'instruire "
                      "la demande %s.") % rec.name
                )
            rec.state = "progress"

    def action_extend(self):
        """Prorogation de deux mois (art. 12.3)."""
        for rec in self:
            if rec.extension_granted:
                raise UserError(_("Le délai a déjà été prorogé pour %s.") % rec.name)
            rec.extension_granted = True
            rec.state = "extended"
            rec.message_post(
                body=_("Délai prorogé de deux mois au titre de l'article 12.3. "
                       "Nouvelle échéance : %s") % rec.date_deadline
            )
        template = self.env.ref(
            "exocoms_rgpd.mail_template_rgpd_extension", raise_if_not_found=False
        )
        if template:
            for rec in self:
                template.send_mail(rec.id, force_send=False)

    def action_generate_export(self):
        """Constitue l'export de données (droit d'accès / portabilité)."""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(
                _("Rattachez la demande à une personne (contact) avant de "
                  "générer l'export.")
            )
        if not self.identity_verified:
            raise UserError(
                _("L'identité doit être vérifiée avant toute communication de "
                  "données personnelles.")
            )
        data = self.env["exocoms.rgpd.engine"].collect_personal_data(self.partner_id)
        payload = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        self.write(
            {
                "export_data": base64.b64encode(payload.encode("utf-8")),
                "export_filename": "donnees-personnelles-%s.json" % self.name.replace("/", "-"),
            }
        )
        self.message_post(
            body=_("Export généré : %s section(s), %s enregistrement(s).")
            % (len(data["sections"]), sum(s["count"] for s in data["sections"]))
        )
        return True

    def action_print_export(self):
        self.ensure_one()
        return self.env.ref("exocoms_rgpd.action_report_rgpd_data_export").report_action(self)

    def action_open_erase_wizard(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Rattachez la demande à un contact."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Effacement des données"),
            "res_model": "exocoms.rgpd.erase.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_request_id": self.id,
            },
        }

    def action_done(self):
        for rec in self:
            if not rec.identity_verified:
                raise UserError(
                    _("Identité non vérifiée : la demande %s ne peut pas être "
                      "clôturée.") % rec.name
                )
            if not rec.response_note:
                raise UserError(
                    _("Documentez la réponse apportée avant de clôturer %s.") % rec.name
                )
            rec.write({"state": "done", "date_response": fields.Datetime.now()})
            rec.activity_unlink(["mail.mail_activity_data_todo"])
        template = self.env.ref(
            "exocoms_rgpd.mail_template_rgpd_response", raise_if_not_found=False
        )
        if template:
            for rec in self:
                template.send_mail(rec.id, force_send=False)

    def action_refuse(self):
        for rec in self:
            if not rec.refusal_ground:
                raise UserError(
                    _("Indiquez le motif de refus : la personne doit être "
                      "informée des voies de recours (art. 12.4).")
                )
            rec.write({"state": "refused", "date_response": fields.Datetime.now()})
            rec.activity_unlink(["mail.mail_activity_data_todo"])

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset(self):
        self.write({"state": "new"})

    def action_print(self):
        return self.env.ref("exocoms_rgpd.action_report_rgpd_request").report_action(self)

    # ------------------------------------------------------------------
    @api.model
    def _cron_check_deadlines(self):
        """Relance les responsables et alerte sur les demandes en retard."""
        today = fields.Date.context_today(self)
        # sudo : le cron doit couvrir toutes les sociétés, pas seulement celles
        # autorisées pour l'utilisateur d'exécution du cron.
        pending = self.sudo().search(
            [("state", "in", ["new", "identity", "progress", "extended"])]
        )
        late = pending.filtered(lambda r: r.date_deadline and r.date_deadline < today)
        soon = pending.filtered(
            lambda r: r.date_deadline and 0 <= (r.date_deadline - today).days <= 7
        )
        for rec in late:
            rec.message_post(
                body=_("<b>Délai légal dépassé</b> depuis le %s. La CNIL peut être "
                       "saisie par la personne concernée.") % rec.date_deadline,
                subtype_xmlid="mail.mt_comment",
            )
        for rec in soon:
            if not rec.activity_ids:
                rec._schedule_activity()
        _logger.info(
            "RGPD: %s demande(s) en retard, %s à échéance proche.", len(late), len(soon)
        )
        return True
