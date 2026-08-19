# -*- coding: utf-8 -*-
"""Propagation du consentement marketing vers la liste noire de messagerie.

Enregistrer un retrait de consentement sans couper les envois n'a aucune valeur
juridique : le journal prouverait seulement que le responsable de traitement
était informé. Ce module fait donc circuler l'information dans les deux sens
entre ``exocoms.rgpd.consent`` et ``mail.blacklist``.

Point d'attention : ``mail.blacklist`` est **global** à la base, alors que les
consentements sont cloisonnés par société. Une adresse n'est donc mise en liste
noire que si elle n'a de consentement marketing accordé dans **aucune** société.
À l'inverse, un consentement accordé dans une seule société suffit à l'en
retirer. Ce choix protège la personne dans le sens qui compte : on ne coupe
jamais un envoi qu'elle a explicitement accepté ailleurs, et on ne réactive
jamais un envoi sur la seule foi d'une entité tierce.
"""

import logging

from odoo import _, api, fields, models, tools

_logger = logging.getLogger(__name__)

# Contexte posé pour empêcher un aller-retour infini entre les deux modèles.
SKIP = "rgpd_skip_blacklist_sync"


class RgpdConsentBlacklist(models.Model):
    _inherit = "exocoms.rgpd.consent"

    # ------------------------------------------------------------------
    # Outils
    # ------------------------------------------------------------------
    @api.model
    def _blacklist_enabled(self, company=None):
        company = company or self.env.company
        return bool(company.sudo().rgpd_blacklist_sync)

    @api.model
    def _marketing_granted_anywhere(self, email):
        """Un consentement marketing est-il accordé pour cette adresse ?

        La recherche est volontairement transverse aux sociétés : la liste
        noire d'Odoo l'est aussi.
        """
        normalized = tools.email_normalize(email)
        if not normalized:
            return False
        latest = {}
        records = self.sudo().search(
            [("email", "=ilike", normalized),
             ("purpose_id.category", "=", "marketing")],
            order="date_event desc, id desc",
        )
        for rec in records:
            key = (rec.company_id.id, rec.purpose_code)
            if key not in latest:
                latest[key] = rec
        return any(rec.state == "granted" for rec in latest.values())

    # ------------------------------------------------------------------
    # Consentement -> liste noire
    # ------------------------------------------------------------------
    def _sync_to_blacklist(self):
        """Aligne ``mail.blacklist`` sur l'état courant des consentements."""
        if self.env.context.get(SKIP):
            return
        Blacklist = self.env.get("mail.blacklist")
        if Blacklist is None:
            return
        Blacklist = Blacklist.sudo().with_context(**{SKIP: True})

        handled = set()
        for rec in self:
            if rec.purpose_id.category != "marketing":
                continue
            if not self._blacklist_enabled(rec.company_id):
                continue
            normalized = tools.email_normalize(rec.email)
            if not normalized or normalized in handled:
                continue
            handled.add(normalized)
            try:
                if self._marketing_granted_anywhere(normalized):
                    Blacklist._remove(
                        normalized,
                        message=_(
                            "Consentement marketing accordé (entrée de journal "
                            "n° %s). Retrait de la liste noire au titre du RGPD."
                        ) % rec.id,
                    )
                else:
                    Blacklist._add(
                        normalized,
                        message=_(
                            "Consentement marketing retiré ou refusé (entrée de "
                            "journal n° %s). Mise en liste noire au titre de "
                            "l'article 7.3 du RGPD."
                        ) % rec.id,
                    )
            except Exception:  # pragma: no cover
                _logger.exception(
                    "RGPD: synchronisation de la liste noire impossible pour %s",
                    normalized,
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_to_blacklist()
        return records

    # ------------------------------------------------------------------
    # Réconciliation périodique
    # ------------------------------------------------------------------
    # Les deux tables peuvent diverger : import massif, restauration de
    # sauvegarde, module tiers écrivant directement, ou simple échec pendant une
    # synchronisation. La réconciliation fait foi du journal des consentements,
    # seule source horodatée et scellée.

    @api.model
    def _divergences(self):
        Consent = self.sudo()
        Blacklist = self.env.get("mail.blacklist")
        if Blacklist is None:
            return []
        emails = set(
            Consent.search(
                [("purpose_id.category", "=", "marketing")]
            ).mapped("email")
        )
        blacklisted = {
            tools.email_normalize(b.email)
            for b in Blacklist.sudo().search([("active", "=", True)])
        }
        out = []
        for raw in emails:
            email = tools.email_normalize(raw)
            if not email:
                continue
            should_send = Consent._marketing_granted_anywhere(email)
            is_blocked = email in blacklisted
            if should_send and is_blocked:
                out.append((email, "blocked_but_consented"))
            elif not should_send and not is_blocked:
                out.append((email, "consent_withdrawn_but_not_blocked"))
        return out

    @api.model
    def _cron_reconcile_blacklist(self):
        Blacklist = self.env.get("mail.blacklist")
        if Blacklist is None:
            return True
        Blacklist = Blacklist.sudo().with_context(**{SKIP: True})
        fixed = 0
        for email, kind in self._divergences():
            try:
                if kind == "blocked_but_consented":
                    Blacklist._remove(email)
                else:
                    Blacklist._add(email)
                fixed += 1
            except Exception:  # pragma: no cover
                _logger.exception("RGPD: réconciliation impossible pour %s", email)
        if fixed:
            _logger.info("RGPD: %s divergence(s) de liste noire corrigée(s).", fixed)
        return True


class MailBlacklist(models.Model):
    """Sens inverse : une désinscription Odoo vaut retrait de consentement.

    Le lien de désinscription des campagnes, la saisie manuelle en liste noire
    et l'import alimentent tous ``mail.blacklist`` sans passer par ce module.
    Sans ce hook, ces retraits ne laisseraient aucune trace dans le journal
    alors qu'ils sont juridiquement des retraits au sens de l'article 7.3.
    """

    _inherit = "mail.blacklist"

    def _rgpd_log(self, granted):
        if self.env.context.get(SKIP):
            return
        Consent = self.env.get("exocoms.rgpd.consent")
        Purpose = self.env.get("exocoms.rgpd.consent.purpose")
        if Consent is None or Purpose is None:
            return
        purposes = Purpose.sudo().search([("category", "=", "marketing")])
        if not purposes:
            return
            
        # Pré-charger toutes les sociétés pour les objectifs globaux
        all_companies = self.env['res.company'].sudo().search([])

        for record in self:
            email = tools.email_normalize(record.email)
            if not email:
                continue
                
            for purpose in purposes:
                # Si l'objectif est lié à une société, on la cible. 
                # Sinon, l'objectif est global : on doit répercuter le retrait sur toutes les sociétés.
                companies_to_check = purpose.company_id or all_companies
                
                for company in companies_to_check:
                    if not Consent._blacklist_enabled(company):
                        continue
                        
                    current = Consent.sudo().get_current_state(
                        email, company=company
                    ).get(purpose.code)
                    
                    is_granted = bool(current and current.state == "granted")
                    if is_granted == granted:
                        continue
                        
                    try:
                        Consent.sudo().with_context(**{SKIP: True}).register(
                            purpose.code,
                            email,
                            granted=granted,
                            state=None if granted else "withdrawn",
                            company=company,
                            method="manual",
                            note=_(
                                "Synchronisation depuis la liste noire de messagerie "
                                "d'Odoo (désinscription, saisie manuelle ou import)."
                            ) if not granted else _(
                                "Retrait de la liste noire de messagerie d'Odoo."
                            ),
                        )
                    except Exception:  # pragma: no cover
                        _logger.exception(
                            "RGPD: journalisation du retrait impossible pour %s", email
                        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # ``_remove()`` crée un enregistrement avec ``active=False`` lorsque
        # l'adresse est inconnue : on ne peut donc pas supposer qu'une création
        # vaut mise en liste noire, il faut lire l'état réel de chaque
        # enregistrement. ``create()`` renvoie de plus les entrées
        # préexistantes, que ce parcours traite correctement puisque
        # ``_rgpd_log`` ignore les états déjà alignés.
        for record in records:
            record._rgpd_log(granted=not record.active)
        return records

    def write(self, vals):
        result = super().write(vals)
        if "active" in vals:
            # active=True signifie « adresse en liste noire », donc consentement
            # retiré ; active=False signifie que l'envoi redevient possible.
            # ``action_archive`` / ``action_unarchive``, utilisés par
            # ``_add`` et ``_remove``, passent bien par ``write``.
            self._rgpd_log(granted=not vals["active"])
        return result

    def unlink(self):
        # La suppression d'une entrée rétablit la possibilité d'envoi : c'est
        # un fait à journaliser au même titre que l'inscription.
        self._rgpd_log(granted=True)
        return super().unlink()