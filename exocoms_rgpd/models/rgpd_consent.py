# -*- coding: utf-8 -*-
"""Journal des consentements : preuve horodatée et inaltérable (art. 7.1)."""

import hashlib
import json
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RgpdConsent(models.Model):
    _name = "exocoms.rgpd.consent"
    _description = "RGPD - Consentement"
    _order = "date_event desc, id desc"
    _rec_name = "email"

    partner_id = fields.Many2one(
        "res.partner", string="Personne concernée", index=True, ondelete="restrict"
    )
    email = fields.Char(string="E-mail", index=True, required=True)
    purpose_id = fields.Many2one(
        "exocoms.rgpd.consent.purpose", string="Finalité", required=True,
        index=True, ondelete="restrict",
    )
    purpose_code = fields.Char(related="purpose_id.code", store=True)
    state = fields.Selection(
        [
            ("granted", "Accordé"),
            ("refused", "Refusé"),
            ("withdrawn", "Retiré"),
            ("expired", "Expiré"),
        ],
        string="État", required=True, default="granted", index=True,
    )
    date_event = fields.Datetime(
        string="Date de l'action", required=True, default=fields.Datetime.now, index=True
    )
    date_expiry = fields.Datetime(string="Expire le", index=True)

    # -- Preuve technique -------------------------------------------------
    method = fields.Selection(
        [
            ("web_form", "Formulaire web"),
            ("cookie_banner", "Bandeau cookies (CMP)"),
            ("portal", "Portail client"),
            ("email_optin", "Double opt-in e-mail"),
            ("paper", "Support papier"),
            ("phone", "Téléphone"),
            ("manual", "Saisie manuelle"),
            ("import", "Import"),
        ],
        string="Méthode de recueil", required=True, default="web_form",
    )
    consent_text = fields.Text(
        string="Libellé accepté", required=True,
        help="Copie figée du texte présenté à la personne au moment du recueil.",
    )
    source_url = fields.Char(string="URL d'origine")
    ip_address = fields.Char(string="Adresse IP")
    user_agent = fields.Char(string="User-Agent")
    external_ref = fields.Char(
        string="Référence externe",
        help="Identifiant fourni par un CMP tiers (Axeptio, tarteaucitron, Didomi...).",
    )
    user_id = fields.Many2one("res.users", string="Enregistré par", default=lambda s: s.env.user)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, index=True
    )
    note = fields.Text(string="Commentaire")

    # -- Intégrité ---------------------------------------------------------
    proof_hash = fields.Char(string="Empreinte SHA-256", readonly=True, copy=False)
    previous_hash = fields.Char(string="Empreinte précédente", readonly=True, copy=False)
    integrity_ok = fields.Boolean(
        string="Intégrité vérifiée", compute="_compute_integrity", store=False
    )

    _rgpd_consent_hash_uniq = models.Constraint(
        "unique(proof_hash)",
        "Une entrée de journal identique existe déjà.",
    )

    # ------------------------------------------------------------------
    @api.depends("partner_id", "email", "purpose_id", "state", "date_event")
    def _compute_display_name(self):
        labels = dict(self._fields["state"]._description_selection(self.env))
        for rec in self:
            who = rec.partner_id.display_name or rec.email or "?"
            rec.display_name = "%s - %s (%s)" % (
                who, rec.purpose_id.name or "", labels.get(rec.state, "")
            )

    def _compute_integrity(self):
        for rec in self:
            rec.integrity_ok = rec.proof_hash == rec._build_hash()

    def _build_hash(self):
        self.ensure_one()
        payload = json.dumps(
            {
                "email": self.email or "",
                "partner": self.partner_id.id or 0,
                "purpose": self.purpose_id.code or "",
                "state": self.state,
                "date": fields.Datetime.to_string(self.date_event) or "",
                "text": self.consent_text or "",
                "ip": self.ip_address or "",
                "ua": self.user_agent or "",
                "prev": self.previous_hash or "",
                "company": self.company_id.id or 0,
            },
            sort_keys=True, ensure_ascii=False,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Chaînage
    # ------------------------------------------------------------------
    def _chain_last(self, company_id, exclude_ids=()):
        """Dernier maillon de la chaîne de la société ``company_id``.

        La recherche est faite en ``sudo`` : sans cela, une création depuis
        l'interface subirait la règle multi-société et scellerait l'entrée sur
        un maillon partiel, ce qui fragmenterait la chaîne. Le chaînage est
        cloisonné par société pour qu'un utilisateur n'ayant accès qu'à une
        entité puisse vérifier l'intégralité de sa propre chaîne.
        """
        domain = [("company_id", "=", company_id or False)]
        if exclude_ids:
            domain.append(("id", "not in", list(exclude_ids)))
        return self.sudo().search(domain, order="id desc", limit=1)

    # ------------------------------------------------------------------
    # Immuabilité du journal
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("consent_text") and vals.get("purpose_id"):
                purpose = self.env["exocoms.rgpd.consent.purpose"].browse(vals["purpose_id"])
                vals["consent_text"] = purpose.consent_text
            if not vals.get("date_expiry") and vals.get("purpose_id"):
                purpose = self.env["exocoms.rgpd.consent.purpose"].browse(vals["purpose_id"])
                if purpose.validity_months:
                    base = fields.Datetime.to_datetime(
                        vals.get("date_event") or fields.Datetime.now()
                    )
                    vals["date_expiry"] = base + relativedelta(months=purpose.validity_months)
        records = super().create(vals_list)
        # Une chaîne distincte par société : on scelle chaque entrée sur le
        # dernier maillon de sa propre entité.
        chain_heads = {}
        for rec in records:
            company_id = rec.company_id.id or False
            if company_id not in chain_heads:
                last = self._chain_last(company_id, exclude_ids=records.ids)
                chain_heads[company_id] = last.proof_hash or ""
            rec.with_context(rgpd_seal=True).previous_hash = chain_heads[company_id]
            digest = rec._build_hash()
            rec.with_context(rgpd_seal=True).proof_hash = digest
            chain_heads[company_id] = digest
        return records

    def write(self, vals):
        sealed = {"email", "purpose_id", "state", "date_event", "consent_text",
                  "ip_address", "user_agent", "proof_hash", "previous_hash",
                  "method", "source_url", "company_id", "partner_id"}
        if not self.env.context.get("rgpd_seal") and sealed.intersection(vals):
            raise UserError(
                _("Le journal des consentements est inaltérable : une entrée ne "
                  "peut pas être modifiée. Enregistrez une nouvelle entrée "
                  "(retrait ou renouvellement) à la place.")
            )
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get("rgpd_force_unlink"):
            raise UserError(
                _("Le journal des consentements ne peut pas être supprimé : il "
                  "constitue la preuve exigée par l'article 7.1 du RGPD.")
            )
        return super().unlink()

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------
    @api.model
    def register(self, purpose_code, email, granted=True, partner=None, **kwargs):
        """Point d'entrée unique pour journaliser un consentement."""
        target_company = kwargs.get("company") or self.env.company
        purpose = self.env["exocoms.rgpd.consent.purpose"]._resolve(
            purpose_code, company=target_company
        )
        if not purpose:
            raise UserError(_("Finalité de consentement inconnue : %s") % purpose_code)
        if not partner and email:
            partner = self.env["res.partner"].sudo().search(
                [("email", "=ilike", email)], limit=1
            )
        # La société est déterminée explicitement : en multi-société le
        # chaînage et les règles d'accès en dépendent, et un appel via ``sudo``
        # ne doit pas laisser la valeur au hasard du contexte.
        company = kwargs.get("company") or self.env.company
        vals = {
            "purpose_id": purpose.id,
            "email": email or (partner and partner.email) or "",
            "partner_id": partner.id if partner else False,
            "state": kwargs.get("state") or ("granted" if granted else "refused"),
            "consent_text": kwargs.get("consent_text") or purpose.consent_text,
            "method": kwargs.get("method", "web_form"),
            "source_url": kwargs.get("source_url"),
            "ip_address": kwargs.get("ip_address"),
            "user_agent": (kwargs.get("user_agent") or "")[:500] or False,
            "external_ref": kwargs.get("external_ref"),
            "note": kwargs.get("note"),
            "company_id": company.id,
        }
        if kwargs.get("date_expiry"):
            vals["date_expiry"] = kwargs["date_expiry"]
        return self.sudo().create(vals)

    @api.model
    def withdraw(self, purpose_code, email, partner=None, **kwargs):
        """Retrait du consentement (art. 7.3).

        L'état définitif est passé à la création : rescelller l'empreinte après
        coup laisserait, le temps d'une transaction, un maillon incohérent dans
        la chaîne.
        """
        kwargs.setdefault("method", "portal")
        kwargs["state"] = "withdrawn"
        return self.register(
            purpose_code, email, granted=False, partner=partner, **kwargs
        )

    @api.model
    def get_current_state(self, email, partner=None, company=None):
        """État courant des consentements pour une personne.

        Le résultat est cloisonné par société : un consentement donné à la
        société A ne vaut pas pour la société B, qui est un responsable de
        traitement distinct. Passer ``company=False`` explicitement pour
        obtenir une vue transverse (usage administratif uniquement).
        """
        domain = [("email", "=ilike", email)] if email else []
        if partner:
            domain = ["|", ("partner_id", "=", partner.id)] + domain if domain else [
                ("partner_id", "=", partner.id)
            ]
        if company is None:
            company = self.env.company
        if company:
            domain = list(domain) + [
                "|", ("company_id", "=", False), ("company_id", "=", company.id)
            ]
        records = self.sudo().search(domain, order="date_event desc, id desc")
        current = {}
        for rec in records:
            if rec.purpose_code not in current:
                current[rec.purpose_code] = rec
        return current

    def action_withdraw(self):
        for rec in self.filtered(lambda r: r.state == "granted"):
            self.withdraw(
                rec.purpose_id.code, rec.email, partner=rec.partner_id, method="manual",
                note=_("Retrait enregistré manuellement par %s") % self.env.user.name,
            )

    def action_check_integrity(self):
        """Contrôle l'empreinte de chaque entrée puis le chaînage par société.

        Le contrôle de chaînage est fait en ``sudo`` sur l'ensemble de la
        chaîne de chaque société représentée dans la sélection : vérifier un
        sous-ensemble ne prouverait rien, une suppression en base laisserait
        les entrées restantes individuellement valides.
        """
        broken = self.filtered(lambda r: r.proof_hash != r._build_hash())
        if broken:
            raise UserError(
                _("Altération détectée sur %s entrée(s) : %s")
                % (len(broken), ", ".join(str(i) for i in broken.ids))
            )

        gaps = []
        checked = 0
        for company_id in set(self.mapped(lambda r: r.company_id.id or False)):
            chain = self.sudo().search(
                [("company_id", "=", company_id or False)], order="id asc"
            )
            previous = ""
            for entry in chain:
                if (entry.previous_hash or "") != previous:
                    gaps.append(entry.id)
                previous = entry.proof_hash or ""
            checked += len(chain)

        if gaps:
            raise UserError(
                _("Rupture de chaînage détectée : le maillon précédent de %s "
                  "entrée(s) ne correspond pas (identifiants %s). Une ou "
                  "plusieurs entrées ont probablement été supprimées "
                  "directement en base de données.")
                % (len(gaps), ", ".join(str(i) for i in gaps))
            )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Intégrité vérifiée"),
                "message": _(
                    "Les %s entrées sélectionnées sont intactes et le chaînage "
                    "des %s entrées des sociétés concernées est continu."
                ) % (len(self), checked),
                "type": "success",
            },
        }

    # ------------------------------------------------------------------
    @api.model
    def _cron_expire_consents(self):
        now = fields.Datetime.now()
        # sudo : le cron doit couvrir toutes les sociétés, pas seulement celles
        # autorisées pour l'utilisateur d'exécution.
        expired = self.sudo().search(
            [("state", "=", "granted"), ("date_expiry", "!=", False),
             ("date_expiry", "<", now)]
        )
        for rec in expired:
            self.sudo().create(
                {
                    "purpose_id": rec.purpose_id.id,
                    "email": rec.email,
                    "partner_id": rec.partner_id.id,
                    "state": "expired",
                    "consent_text": rec.consent_text,
                    "method": "manual",
                    # La nouvelle entrée reste dans la chaîne de la société
                    # d'origine.
                    "company_id": rec.company_id.id,
                    "note": _("Expiration automatique du consentement du %s")
                    % fields.Datetime.to_string(rec.date_event),
                }
            )
        if expired:
            _logger.info("RGPD: %s consentement(s) expiré(s).", len(expired))
        return True
