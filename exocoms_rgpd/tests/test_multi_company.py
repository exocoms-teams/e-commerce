# -*- coding: utf-8 -*-
"""Cloisonnement multi-société : finalités, séquences, règles d'accès."""

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import RgpdCommon


@tagged("post_install", "-at_install", "rgpd")
class TestMultiCompany(RgpdCommon):

    def test_own_purpose_overrides_shared_one(self):
        """Une finalité propre à une société prime sur la finalité partagée."""
        own = self.Purpose.create(
            {
                "name": "Newsletter société B",
                "code": self.purpose_shared.code,
                "category": "marketing",
                "consent_text": "Texte propre à la société B.",
                "company_id": self.company_b.id,
            }
        )
        resolved_a = self.Purpose._resolve(
            self.purpose_shared.code, company=self.company_a
        )
        resolved_b = self.Purpose._resolve(
            self.purpose_shared.code, company=self.company_b
        )
        self.assertEqual(resolved_a, self.purpose_shared)
        self.assertEqual(resolved_b, own)

    def test_consent_freezes_the_company_specific_text(self):
        """La preuve doit figer le texte réellement présenté à la personne."""
        self.Purpose.create(
            {
                "name": "Newsletter société B",
                "code": self.purpose_shared.code,
                "category": "marketing",
                "consent_text": "Texte propre à la société B.",
                "company_id": self.company_b.id,
            }
        )
        consent = self._consent(self.company_b)
        self.assertEqual(consent.consent_text, "Texte propre à la société B.")

    def test_applicable_purposes_exclude_other_companies(self):
        self.Purpose.create(
            {
                "name": "Offre société B",
                "code": "test_offre_b",
                "category": "marketing",
                "consent_text": "Offre réservée à la société B.",
                "company_id": self.company_b.id,
            }
        )
        codes_a = self.Purpose._applicable(company=self.company_a).mapped("code")
        codes_b = self.Purpose._applicable(company=self.company_b).mapped("code")
        self.assertNotIn("test_offre_b", codes_a)
        self.assertIn("test_offre_b", codes_b)
        self.assertIn(self.purpose_shared.code, codes_a)

    def test_applicable_purposes_have_no_duplicate_code(self):
        self.Purpose.create(
            {
                "name": "Newsletter société B",
                "code": self.purpose_shared.code,
                "category": "marketing",
                "consent_text": "Texte propre à la société B.",
                "company_id": self.company_b.id,
            }
        )
        codes = self.Purpose._applicable(company=self.company_b).mapped("code")
        self.assertEqual(
            len(codes), len(set(codes)),
            "Une surcharge ne doit pas faire apparaître deux fois le même code.",
        )

    def test_shared_purpose_code_is_unique(self):
        """PostgreSQL considère deux NULL comme distincts : le contrôle Python
        est le seul rempart pour les finalités partagées."""
        with self.assertRaises(ValidationError):
            self.Purpose.create(
                {
                    "name": "Doublon partagé",
                    "code": self.purpose_shared.code,
                    "category": "marketing",
                    "consent_text": "Doublon.",
                }
            )

    def test_sequences_are_shared_by_default(self):
        req_a = self.Request.with_company(self.company_a).create(
            {"requester_name": "A", "email": "a@exemple.fr", "request_type": "access"}
        )
        req_b = self.Request.with_company(self.company_b).create(
            {"requester_name": "B", "email": "b@exemple.fr", "request_type": "access"}
        )
        self.assertNotEqual(
            req_a.name, req_b.name,
            "Les références doivent rester uniques sur la séquence partagée.",
        )

    def test_company_specific_sequences_restart_numbering(self):
        self.Request.with_company(self.company_a).create(
            {"requester_name": "A", "email": "a@exemple.fr", "request_type": "access"}
        )
        created = self.company_b._rgpd_create_sequences()
        self.assertEqual(len(created), 3, "Trois séquences doivent être créées.")
        self.assertTrue(self.company_b._rgpd_has_own_sequences())
        req_b = self.Request.with_company(self.company_b).create(
            {"requester_name": "B", "email": "b@exemple.fr", "request_type": "access"}
        )
        self.assertTrue(req_b.name.endswith("0001"))

    def test_sequence_creation_is_idempotent(self):
        self.company_b._rgpd_create_sequences()
        again = self.company_b._rgpd_create_sequences()
        self.assertFalse(
            again, "Un second appel ne doit rien créer ni réinitialiser un compteur."
        )
