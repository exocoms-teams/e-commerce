# -*- coding: utf-8 -*-
"""Intégrité et immuabilité du journal des consentements."""

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import RgpdCommon


@tagged("post_install", "-at_install", "rgpd")
class TestConsentChain(RgpdCommon):

    def test_chain_is_sealed_on_create(self):
        first = self._consent(self.company_a)
        second = self._consent(self.company_a, granted=False)
        self.assertTrue(first.proof_hash, "Une entrée doit être scellée à la création.")
        self.assertEqual(
            second.previous_hash,
            first.proof_hash,
            "Chaque entrée doit sceller l'empreinte de la précédente.",
        )

    def test_chain_is_isolated_per_company(self):
        """Deux sociétés tiennent deux chaînes indépendantes.

        C'est la régression la plus coûteuse : une chaîne commune se
        fragmenterait dès qu'un utilisateur mono-société crée une entrée depuis
        l'interface, et la vérification d'intégrité deviendrait ininterprétable.
        """
        a1 = self._consent(self.company_a)
        b1 = self._consent(self.company_b)
        a2 = self._consent(self.company_a, granted=False)

        self.assertEqual(a1.previous_hash or "", "")
        self.assertEqual(b1.previous_hash or "", "")
        self.assertEqual(a2.previous_hash, a1.proof_hash)
        self.assertNotEqual(
            a2.previous_hash, b1.proof_hash,
            "La chaîne de la société A ne doit pas passer par la société B.",
        )

    def test_write_is_forbidden_on_sealed_fields(self):
        consent = self._consent(self.company_a)
        for field, value in (
            ("state", "withdrawn"),
            ("email", "autre@exemple.fr"),
            ("consent_text", "Texte réécrit"),
            ("company_id", self.company_b.id),
        ):
            with self.assertRaises(
                UserError, msg="Le champ %s doit être scellé." % field
            ):
                consent.write({field: value})

    def test_unlink_is_forbidden(self):
        consent = self._consent(self.company_a)
        with self.assertRaises(UserError):
            consent.unlink()

    def test_integrity_check_passes_on_clean_chain(self):
        records = self.Consent
        for _i in range(3):
            records |= self._consent(self.company_a)
        # Ne lève pas : la chaîne est continue et chaque empreinte est valide.
        records.action_check_integrity()

    def test_integrity_check_detects_database_tampering(self):
        """Une modification faite en SQL doit être détectée.

        C'est tout l'intérêt du scellement : l'ORM protège déjà par ``write``,
        seul un accès direct à la base peut altérer une entrée.
        """
        consent = self._consent(self.company_a)
        self.env.cr.execute(
            "UPDATE exocoms_rgpd_consent SET email = %s WHERE id = %s",
            ("falsifie@exemple.fr", consent.id),
        )
        consent.invalidate_recordset()
        with self.assertRaises(UserError):
            consent.action_check_integrity()

    def test_integrity_check_detects_deleted_entry(self):
        """Une suppression en base rompt le chaînage sans altérer les entrées."""
        first = self._consent(self.company_a)
        second = self._consent(self.company_a, granted=False)
        third = self._consent(self.company_a)
        self.env.cr.execute(
            "DELETE FROM exocoms_rgpd_consent WHERE id = %s", (second.id,)
        )
        self.env.invalidate_all()
        remaining = first | third
        with self.assertRaises(UserError):
            remaining.action_check_integrity()

    def test_withdraw_creates_entry_without_resealing(self):
        self._consent(self.company_a)
        withdrawn = self.Consent.withdraw(
            self.purpose_shared.code,
            self.partner.email,
            partner=self.partner,
            company=self.company_a,
        )
        self.assertEqual(withdrawn.state, "withdrawn")
        self.assertEqual(
            withdrawn.proof_hash,
            withdrawn._build_hash(),
            "L'empreinte doit correspondre à l'état définitif de l'entrée.",
        )

    def test_get_current_state_is_company_scoped(self):
        self._consent(self.company_a, granted=True)
        self._consent(self.company_b, granted=False)
        state_a = self.Consent.get_current_state(
            self.partner.email, self.partner, company=self.company_a
        )
        state_b = self.Consent.get_current_state(
            self.partner.email, self.partner, company=self.company_b
        )
        self.assertEqual(state_a[self.purpose_shared.code].state, "granted")
        self.assertEqual(state_b[self.purpose_shared.code].state, "refused")
