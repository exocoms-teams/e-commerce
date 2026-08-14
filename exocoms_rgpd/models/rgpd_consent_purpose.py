# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RgpdConsentPurpose(models.Model):
    """Finalité pour laquelle un consentement est recueilli (art. 4.11 et 7)."""

    _name = "exocoms.rgpd.consent.purpose"
    _description = "RGPD - Finalité de consentement"
    _order = "sequence, name"

    name = fields.Char(string="Finalité", required=True, translate=True)
    code = fields.Char(
        string="Code", required=True,
        help="Identifiant technique utilisé par le portail et les CMP externes "
        "(ex. newsletter, cookies_analytics, cookies_marketing).",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Html(string="Description affichée", translate=True, sanitize=True)
    consent_text = fields.Text(
        string="Libellé du consentement", required=True, translate=True,
        help="Texte exact présenté à la personne. Il est figé dans chaque "
        "enregistrement de consentement afin de constituer une preuve.",
    )
    category = fields.Selection(
        [
            ("marketing", "Prospection / marketing"),
            ("cookies", "Cookies et traceurs"),
            ("profiling", "Profilage"),
            ("transfer", "Transfert de données"),
            ("other", "Autre"),
        ],
        string="Catégorie", default="marketing", required=True,
    )
    essential = fields.Boolean(
        string="Strictement nécessaire",
        help="Cochez pour les finalités exemptées de consentement (cookies "
        "strictement nécessaires au service). Aucune case ne sera proposée.",
    )
    portal_visible = fields.Boolean(
        string="Visible sur le portail", default=True,
        help="La personne peut accorder ou retirer ce consentement depuis "
        "/my/privacy.",
    )
    default_granted = fields.Boolean(
        string="Coché par défaut",
        help="À n'activer que pour les finalités essentielles. Le consentement "
        "RGPD doit résulter d'un acte positif clair.",
    )
    validity_months = fields.Integer(
        string="Durée de validité (mois)", default=13,
        help="Recommandation CNIL : 13 mois pour les cookies. 0 = sans expiration.",
    )
    treatment_ids = fields.Many2many(
        "exocoms.rgpd.treatment", string="Traitements concernés"
    )
    consent_count = fields.Integer(compute="_compute_consent_count", string="Consentements")
    granted_count = fields.Integer(compute="_compute_consent_count", string="Accordés")

    company_id = fields.Many2one(
        "res.company", string="Société",
        help="Laissez vide pour une finalité partagée par toutes les sociétés. "
        "Renseignez une société lorsque le libellé de consentement ou la durée "
        "de validité diffèrent d'une entité à l'autre : une finalité propre à "
        "une société prime alors sur la finalité partagée de même code.",
    )

    _rgpd_purpose_code_uniq = models.Constraint(
        "unique(code, company_id)",
        "Ce code de finalité existe déjà pour cette société.",
    )

    @api.constrains("code", "company_id")
    def _check_code_unique(self):
        """Complète la contrainte SQL sur le cas des finalités partagées.

        PostgreSQL considère deux NULL comme distincts : ``unique(code,
        company_id)`` laisserait donc passer plusieurs finalités partagées de
        même code, ce qui rendrait la résolution ambiguë et la preuve de
        consentement contestable.
        """
        for rec in self:
            domain = [("code", "=", rec.code), ("id", "!=", rec.id)]
            if rec.company_id:
                domain.append(("company_id", "=", rec.company_id.id))
            else:
                domain.append(("company_id", "=", False))
            if self.sudo().with_context(active_test=False).search_count(domain):
                raise ValidationError(
                    _("Le code de finalité « %s » est déjà utilisé %s.")
                    % (
                        rec.code,
                        _("par la société %s") % rec.company_id.name
                        if rec.company_id
                        else _("par une finalité partagée"),
                    )
                )

    @api.model
    def _resolve(self, code, company=None):
        """Retourne la finalité applicable à ``company`` pour ce ``code``.

        Une finalité propre à la société l'emporte sur la finalité partagée,
        ce qui permet de personnaliser le libellé de consentement par entité
        sans dupliquer toute la configuration.
        """
        company = company or self.env.company
        candidates = self.sudo().search(
            [("code", "=", code), ("company_id", "in", [company.id, False])]
        )
        # Le tri est fait en Python : sur un many2one nullable, l'ordre SQL
        # dépend du placement des NULL et du tri du comodèle.
        own = candidates.filtered(lambda p: p.company_id.id == company.id)
        return own[:1] or candidates[:1]

    @api.model
    def _applicable(self, company=None, extra_domain=None):
        """Finalités applicables à ``company``, dédoublonnées par code.

        Une société ne doit jamais voir les finalités propres à une autre
        entité, et lorsqu'une finalité propre surcharge une finalité partagée
        de même code, seule la première est retournée.
        """
        company = company or self.env.company
        domain = [("company_id", "in", [company.id, False])]
        if extra_domain:
            domain += list(extra_domain)
        candidates = self.sudo().search(domain)
        by_code = {}
        for purpose in candidates:
            existing = by_code.get(purpose.code)
            if existing is None or (
                not existing.company_id and purpose.company_id.id == company.id
            ):
                by_code[purpose.code] = purpose
        result = self.browse([p.id for p in by_code.values()])
        return result.sorted(lambda p: (p.sequence, p.name or ""))

    def _compute_consent_count(self):
        Consent = self.env["exocoms.rgpd.consent"]
        for rec in self:
            rec.consent_count = Consent.search_count([("purpose_id", "=", rec.id)])
            rec.granted_count = Consent.search_count(
                [("purpose_id", "=", rec.id), ("state", "=", "granted")]
            )

    @api.constrains("default_granted", "essential")
    def _check_default_granted(self):
        for rec in self:
            if rec.default_granted and not rec.essential:
                raise ValidationError(
                    _("Seules les finalités strictement nécessaires peuvent être "
                      "cochées par défaut : le consentement doit résulter d'un "
                      "acte positif clair (art. 4.11 du RGPD).")
                )

    def action_view_consents(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Consentements - %s") % self.name,
            "res_model": "exocoms.rgpd.consent",
            "view_mode": "list,form",
            "domain": [("purpose_id", "=", self.id)],
            "context": {"default_purpose_id": self.id},
        }
