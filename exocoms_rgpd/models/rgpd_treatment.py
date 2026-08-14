# -*- coding: utf-8 -*-
"""Registre des activités de traitement - article 30 du RGPD."""

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

LEGAL_BASIS = [
    ("consent", "Consentement (art. 6.1.a)"),
    ("contract", "Exécution d'un contrat (art. 6.1.b)"),
    ("legal", "Obligation légale (art. 6.1.c)"),
    ("vital", "Sauvegarde des intérêts vitaux (art. 6.1.d)"),
    ("public", "Mission d'intérêt public (art. 6.1.e)"),
    ("legitimate", "Intérêt légitime (art. 6.1.f)"),
]


class RgpdTreatment(models.Model):
    _name = "exocoms.rgpd.treatment"
    _description = "RGPD - Traitement de données (registre art. 30)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "reference desc, id desc"

    # -- Identification ------------------------------------------------
    name = fields.Char(string="Nom du traitement", required=True, tracking=True)
    reference = fields.Char(
        string="Référence", required=True, copy=False, readonly=True,
        default=lambda self: _("Nouveau"), index=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", string="Société", required=True,
        default=lambda self: self.env.company, index=True,
    )
    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("review", "En revue"),
            ("active", "Actif"),
            ("suspended", "Suspendu"),
            ("closed", "Clôturé"),
        ],
        string="État", default="draft", required=True, tracking=True,
    )
    color = fields.Integer()

    # -- Responsabilités -----------------------------------------------
    controller_name = fields.Char(
        string="Responsable de traitement",
        compute="_compute_controller_name", store=True, readonly=False, tracking=True,
    )
    dpo_user_id = fields.Many2one(
        "res.users", string="DPO / Référent", tracking=True,
        default=lambda self: self.env.company.rgpd_dpo_user_id,
    )
    owner_user_id = fields.Many2one(
        "res.users", string="Responsable opérationnel", tracking=True,
        default=lambda self: self.env.user,
    )
    department = fields.Char(string="Service concerné")

    # -- Finalités et licéité ------------------------------------------
    purpose = fields.Html(string="Finalité(s)", sanitize=True)
    legal_basis = fields.Selection(
        LEGAL_BASIS, string="Base légale", required=True,
        default="contract", tracking=True,
    )
    legal_basis_detail = fields.Text(
        string="Justification de la base légale",
        help="Obligatoire pour l'intérêt légitime : décrire la mise en balance "
        "des intérêts (test de proportionnalité).",
    )
    consent_purpose_ids = fields.Many2many(
        "exocoms.rgpd.consent.purpose", string="Finalités de consentement liées",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    # -- Données --------------------------------------------------------
    data_category_ids = fields.Many2many(
        "exocoms.rgpd.data.category", string="Catégories de données", required=True
    )
    has_sensitive_data = fields.Boolean(
        string="Données sensibles", compute="_compute_has_sensitive_data", store=True
    )
    sensitive_justification = fields.Text(string="Exception de l'article 9 invoquée")
    subject_category_ids = fields.Many2many(
        "exocoms.rgpd.subject.category", string="Personnes concernées", required=True
    )
    concerns_minors = fields.Boolean(
        compute="_compute_concerns_minors", store=True, string="Concerne des mineurs"
    )
    estimated_volume = fields.Integer(string="Volume estimé de personnes")
    data_source = fields.Selection(
        [
            ("direct", "Collecte directe auprès de la personne"),
            ("indirect", "Collecte indirecte (tiers, achat de fichier)"),
            ("mixed", "Mixte"),
        ],
        string="Origine des données", default="direct",
    )
    model_ids = fields.Many2many(
        "ir.model", string="Modèles Odoo concernés",
        domain=[("transient", "=", False)],
    )

    # -- Destinataires et transferts ------------------------------------
    recipient_ids = fields.Many2many(
        "exocoms.rgpd.recipient", string="Destinataires",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    transfer_outside_eu = fields.Boolean(
        string="Transfert hors UE/EEE",
        compute="_compute_transfer_outside_eu", store=True, readonly=False,
        tracking=True,
    )
    transfer_country_ids = fields.Many2many(
        "res.country", string="Pays de destination"
    )
    transfer_safeguard = fields.Text(string="Garanties encadrant le transfert")

    # -- Conservation ----------------------------------------------------
    retention_value = fields.Integer(string="Durée de conservation", default=3)
    retention_unit = fields.Selection(
        [("day", "Jour(s)"), ("month", "Mois"), ("year", "An(s)")],
        string="Unité", default="year", required=True,
    )
    retention_start = fields.Char(
        string="Point de départ",
        default="Dernier contact / fin de la relation contractuelle",
    )
    retention_note = fields.Text(string="Précisions sur la conservation")
    retention_rule_ids = fields.One2many(
        "exocoms.rgpd.retention.rule", "treatment_id", string="Règles automatiques"
    )
    retention_rule_count = fields.Integer(compute="_compute_counts")

    # -- Sécurité --------------------------------------------------------
    security_measures = fields.Html(
        string="Mesures de sécurité (art. 32)", sanitize=True,
        default="<ul><li>Contrôle d'accès nominatif et droits granulaires</li>"
        "<li>Authentification à deux facteurs pour les comptes à privilèges</li>"
        "<li>Chiffrement TLS en transit et chiffrement au repos</li>"
        "<li>Sauvegardes quotidiennes chiffrées et testées</li>"
        "<li>Journalisation des accès et des modifications</li></ul>",
    )
    subcontracting = fields.Boolean(string="Recours à un sous-traitant")

    # -- AIPD / DPIA -----------------------------------------------------
    dpia_required = fields.Boolean(string="AIPD requise", tracking=True)
    dpia_done = fields.Boolean(string="AIPD réalisée")
    dpia_date = fields.Date(string="Date de l'AIPD")
    dpia_conclusion = fields.Text(string="Conclusion de l'AIPD")
    risk_level = fields.Selection(
        [("low", "Faible"), ("medium", "Modéré"), ("high", "Élevé")],
        string="Niveau de risque résiduel", default="low", tracking=True,
    )

    # -- Suivi ------------------------------------------------------------
    date_start = fields.Date(string="Mise en œuvre", default=fields.Date.context_today)
    date_review = fields.Date(string="Prochaine revue")
    date_end = fields.Date(string="Fin du traitement")
    review_overdue = fields.Boolean(compute="_compute_review_overdue", search="_search_review_overdue")
    note = fields.Html(string="Notes internes")

    _rgpd_treatment_reference_uniq = models.Constraint(
        "unique(reference, company_id)",
        "Cette référence de traitement existe déjà.",
    )

    # ------------------------------------------------------------------
    # Calculs
    # ------------------------------------------------------------------
    @api.depends("company_id")
    def _compute_controller_name(self):
        for rec in self:
            rec.controller_name = rec.company_id.name

    @api.depends("data_category_ids.sensitive")
    def _compute_has_sensitive_data(self):
        for rec in self:
            rec.has_sensitive_data = any(rec.data_category_ids.mapped("sensitive"))

    @api.depends("subject_category_ids.minor")
    def _compute_concerns_minors(self):
        for rec in self:
            rec.concerns_minors = any(rec.subject_category_ids.mapped("minor"))

    @api.depends("recipient_ids.outside_eu")
    def _compute_transfer_outside_eu(self):
        for rec in self:
            rec.transfer_outside_eu = any(rec.recipient_ids.mapped("outside_eu"))

    @api.depends("retention_rule_ids")
    def _compute_counts(self):
        for rec in self:
            rec.retention_rule_count = len(rec.retention_rule_ids)

    def _compute_review_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.review_overdue = bool(rec.date_review and rec.date_review < today)

    def _search_review_overdue(self, operator, value):
        today = fields.Date.context_today(self)
        overdue = [("date_review", "<", today), ("date_review", "!=", False)]
        if (operator == "=" and value) or (operator == "!=" and not value):
            return overdue
        return ["|", ("date_review", "=", False), ("date_review", ">=", today)]

    @api.depends("name", "reference")
    def _compute_display_name(self):
        for rec in self:
            if rec.reference and rec.reference != _("Nouveau"):
                rec.display_name = "%s - %s" % (rec.reference, rec.name or "")
            else:
                rec.display_name = rec.name or ""

    # ------------------------------------------------------------------
    # Contraintes
    # ------------------------------------------------------------------
    @api.constrains("legal_basis", "legal_basis_detail")
    def _check_legitimate_interest(self):
        for rec in self:
            if rec.legal_basis == "legitimate" and not rec.legal_basis_detail:
                raise ValidationError(
                    _("L'intérêt légitime impose de documenter la mise en balance "
                      "des intérêts dans le champ « Justification de la base légale ».")
                )

    @api.constrains("has_sensitive_data", "sensitive_justification")
    def _check_sensitive(self):
        for rec in self:
            if rec.has_sensitive_data and rec.state == "active" and not rec.sensitive_justification:
                raise ValidationError(
                    _("Un traitement de données sensibles ne peut être activé sans "
                      "préciser l'exception de l'article 9 du RGPD invoquée.")
                )

    @api.constrains("retention_value")
    def _check_retention(self):
        for rec in self:
            if rec.retention_value < 0:
                raise ValidationError(_("La durée de conservation ne peut être négative."))

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("reference") or vals["reference"] == _("Nouveau"):
                company_id = vals.get("company_id", self.env.company.id)
                vals["reference"] = (
                    self.env["ir.sequence"]
                    .with_company(company_id)
                    .next_by_code("exocoms.rgpd.treatment")
                    or _("Nouveau")
                )
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_review(self):
        self.write({"state": "review"})

    def action_activate(self):
        for rec in self:
            if rec.dpia_required and not rec.dpia_done:
                raise ValidationError(
                    _("Le traitement « %s » nécessite une AIPD réalisée avant "
                      "activation.") % rec.name
                )
        self.write({"state": "active"})
        for rec in self.filtered(lambda r: not r.date_review):
            rec.date_review = fields.Date.context_today(rec) + relativedelta(years=1)

    def action_suspend(self):
        self.write({"state": "suspended"})

    def action_close(self):
        self.write({"state": "closed", "date_end": fields.Date.context_today(self)})

    def action_draft(self):
        self.write({"state": "draft"})

    def action_view_retention_rules(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Règles de conservation"),
            "res_model": "exocoms.rgpd.retention.rule",
            "view_mode": "list,form",
            "domain": [("treatment_id", "=", self.id)],
            "context": {"default_treatment_id": self.id},
        }

    def action_print_register(self):
        return self.env.ref(
            "exocoms_rgpd.action_report_rgpd_register"
        ).report_action(self)

    @api.model
    def action_print_full_register(self):
        """Édite le registre consolidé de la société courante.

        Seuls les traitements actifs, en revue ou suspendus sont retenus : un
        traitement en brouillon n'est pas encore mis en œuvre, et un traitement
        clôturé n'a plus à figurer au registre courant — il reste consultable
        dans l'historique.
        """
        treatments = self.search(
            [("state", "in", ["review", "active", "suspended"])],
            order="reference, id",
        )
        if not treatments:
            raise UserError(
                _("Aucun traitement à éditer. Le registre ne reprend que les "
                  "traitements en revue, actifs ou suspendus.")
            )
        return self.env.ref(
            "exocoms_rgpd.action_report_rgpd_register_full"
        ).report_action(treatments)

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------
    def retention_display(self):
        self.ensure_one()
        if not self.retention_value:
            return _("Non définie")
        units = {"day": _("jour(s)"), "month": _("mois"), "year": _("an(s)")}
        return "%s %s" % (self.retention_value, units.get(self.retention_unit, ""))
