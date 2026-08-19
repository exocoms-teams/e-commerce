# -*- coding: utf-8 -*-
"""Propagation consentement marketing <-> liste noire de messagerie."""

from odoo import tools
from odoo.tests import tagged

from .common import RgpdCommon


@tagged("post_install", "-at_install", "rgpd")
class TestBlacklistSync(RgpdCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Blacklist = cls.env["mail.blacklist"]
        cls.email = tools.email_normalize(cls.partner.email)

    def _is_blacklisted(self):
        record = self.Blacklist.sudo().with_context(active_test=False).search(
            [("email", "=", self.email)], limit=1
        )
        return bool(record and record.active)

    def test_withdrawal_blocks_future_mailings(self):
        """Le cœur du sujet : un retrait doit couper la campagne suivante.

        Sans cette propagation, le journal prouverait seulement que le
        responsable de traitement était informé du retrait.
        """
        self._consent(self.company_a, granted=True)
        self.assertFalse(self._is_blacklisted())
        self._consent(self.company_a, granted=False)
        self.assertTrue(self._is_blacklisted())

    def test_new_consent_lifts_the_block(self):
        self._consent(self.company_a, granted=False)
        self.assertTrue(self._is_blacklisted())
        self._consent(self.company_a, granted=True)
        self.assertFalse(self._is_blacklisted())

    def test_non_marketing_purpose_does_not_touch_blacklist(self):
        """Un refus de cookies n'a rien à voir avec la prospection."""
        self._consent(self.company_a, purpose=self.purpose_cookies, granted=False)
        self.assertFalse(self._is_blacklisted())

    def test_blacklist_is_global_across_companies(self):
        """La liste noire d'Odoo est commune : un seul accord suffit à envoyer.

        Bloquer une adresse alors qu'une autre entité détient un consentement
        valide reviendrait à ignorer ce consentement.
        """
        self._consent(self.company_a, granted=True)
        self._consent(self.company_b, granted=True)
        self._consent(self.company_a, granted=False)
        self.assertFalse(
            self._is_blacklisted(),
            "La société B dispose encore d'un consentement accordé.",
        )
        self._consent(self.company_b, granted=False)
        self.assertTrue(
            self._is_blacklisted(),
            "Plus aucune société n'a de consentement : l'adresse doit être bloquée.",
        )

    def test_unsubscribe_is_logged_as_withdrawal(self):
        """Sens inverse : un clic sur « se désinscrire » doit laisser une preuve."""
        self._consent(self.company_a, granted=True)
        before = self.Consent.sudo().search_count([("email", "=ilike", self.email)])
        
        # Action : ajout à la liste noire
        self.Blacklist.sudo()._add(self.email)
        
        # FORCER L'ÉCRITURE EN BASE AVANT LE COMPTAGE
        self.env.flush_all()
        
        after = self.Consent.sudo().search_count([("email", "=ilike", self.email)])
        
        self.assertGreater(
            after, before, f"La désinscription doit créer une entrée de journal. {after} {before}"
        )
        state = self.Consent.get_current_state(
            self.email, company=self.company_a
        ).get(self.purpose_shared.code)
        self.assertEqual(state.state, "withdrawn")

    def test_remove_on_unknown_email_is_not_logged_as_withdrawal(self):
        """``_remove()`` crée une entrée inactive quand l'adresse est inconnue.

        Supposer que toute création vaut mise en liste noire journaliserait un
        retrait à chaque déblocage d'une adresse jamais vue.
        """
        unknown = "inconnu@exemple.fr"
        self.Blacklist.sudo()._remove(unknown)
        state = self.Consent.get_current_state(
            unknown, company=self.company_a
        ).get(self.purpose_shared.code)
        self.assertNotEqual(
            state and state.state, "withdrawn",
            "Un déblocage ne doit pas être journalisé comme un retrait.",
        )

    def test_reconciliation_fixes_divergence(self):
        self._consent(self.company_a, granted=False)
        # Divergence introduite hors module (import, restauration de sauvegarde).
        record = self.Blacklist.sudo().with_context(active_test=False).search(
            [("email", "=", self.email)], limit=1
        )
        record.with_context(rgpd_skip_blacklist_sync=True).action_archive()
        self.assertFalse(self._is_blacklisted())

        self.Consent._cron_reconcile_blacklist()
        self.assertTrue(
            self._is_blacklisted(),
            "La réconciliation doit faire foi du journal des consentements.",
        )

    def test_sync_can_be_disabled_per_company(self):
        self.company_a.rgpd_blacklist_sync = False
        self._consent(self.company_a, granted=False)
        self.assertFalse(self._is_blacklisted())