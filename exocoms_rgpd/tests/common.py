# -*- coding: utf-8 -*-
"""Socle commun aux tests du module RGPD."""

from odoo.tests.common import TransactionCase


class RgpdCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env["res.company"].create({"name": "RGPD Société A"})
        cls.company_b = cls.env["res.company"].create({"name": "RGPD Société B"})

        cls.Consent = cls.env["exocoms.rgpd.consent"]
        cls.Purpose = cls.env["exocoms.rgpd.consent.purpose"]
        cls.Request = cls.env["exocoms.rgpd.request"]
        cls.Rule = cls.env["exocoms.rgpd.retention.rule"]
        cls.Engine = cls.env["exocoms.rgpd.engine"]

        # Finalité marketing partagée par toutes les sociétés.
        cls.purpose_shared = cls.Purpose.create(
            {
                "name": "Newsletter (test)",
                "code": "test_newsletter",
                "category": "marketing",
                "consent_text": "J'accepte de recevoir la newsletter.",
            }
        )
        # Finalité cookies, non marketing : elle ne doit jamais toucher la
        # liste noire de messagerie.
        cls.purpose_cookies = cls.Purpose.create(
            {
                "name": "Mesure d'audience (test)",
                "code": "test_analytics",
                "category": "cookies",
                "consent_text": "J'accepte la mesure d'audience.",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {"name": "Jean Testeur", "email": "jean.testeur@exemple.fr"}
        )

    def _consent(self, company, purpose=None, granted=True, email=None):
        """Enregistre un consentement pour une société donnée."""
        purpose = purpose or self.purpose_shared
        return self.Consent.register(
            purpose.code,
            email or self.partner.email,
            granted=granted,
            partner=self.partner,
            company=company,
        )
