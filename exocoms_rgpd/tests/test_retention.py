# -*- coding: utf-8 -*-
"""Politique de conservation : cloisonnement société et obligations légales."""

from odoo.tests import tagged

from .common import RgpdCommon


@tagged("post_install", "-at_install", "rgpd")
class TestRetention(RgpdCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_partner = cls.env["ir.model"]._get("res.partner")
        cls.field_create_date = cls.env["ir.model.fields"]._get(
            "res.partner", "create_date"
        )

    def _rule(self, company=None, action_type="anonymize"):
        vals = {
            "name": "Purge de test",
            "model_id": self.model_partner.id,
            "date_field_id": self.field_create_date.id,
            "retention_value": 1,
            "retention_unit": "day",
            "action_type": action_type,
            "company_id": company.id if company else False,
        }

        if action_type == "anonymize":
            vals["field_ids"] = [
                (0, 0, {
                    "field_id": self.field_email.id,
                    "strategy": "clear",
                }),
            ]

        return self.Rule.create(vals)

    def test_domain_is_scoped_to_rule_company(self):
        """Régression critique : une règle ne doit jamais purger une autre société.

        Sans ce filtre, activer ``auto_run`` sur une règle de la société A
        anonymiserait aussi les contacts de la société B — perte de données
        irréversible et silencieuse.
        """
        rule = self._rule(company=self.company_a)
        domain = rule._build_domain()
        self.assertIn(
            ("company_id", "=", self.company_a.id), domain,
            "Le domaine doit restreindre la purge à la société de la règle.",
        )
        self.assertIn("|", domain, "Les enregistrements sans société restent inclus.")

    def test_shared_rule_covers_all_companies(self):
        rule = self._rule(company=False)
        domain = rule._build_domain()
        self.assertNotIn(
            "|", domain,
            "Une règle sans société ne doit poser aucun filtre de société.",
        )

    def test_rule_does_not_match_other_company_records(self):
        partner_a = self.env["res.partner"].create(
            {"name": "Contact A", "company_id": self.company_a.id}
        )
        partner_b = self.env["res.partner"].create(
            {"name": "Contact B", "company_id": self.company_b.id}
        )
        self.env.cr.execute(
            "UPDATE res_partner SET create_date = now() - interval '30 days' "
            "WHERE id IN %s",
            ((partner_a.id, partner_b.id),),
        )
        self.env.invalidate_all()

        rule = self._rule(company=self.company_a)
        matched = self.env["res.partner"].sudo().search(rule._build_domain())
        self.assertIn(partner_a, matched)
        self.assertNotIn(
            partner_b, matched,
            "Le contact de la société B ne doit jamais être concerné.",
        )

    def test_legal_hold_blocks_anonymization(self):
        """Les données sous obligation légale de conservation sont préservées."""
        data_map = self.env["exocoms.rgpd.data.map"].sudo().search(
            [("model_name", "=", "res.partner")], limit=1
        )
        if not data_map:
            self.skipTest("Cartographie res.partner absente.")
        data_map.write(
            {"legal_hold": True, "legal_hold_note": "Obligation comptable (test)"}
        )
        report = self.Engine.anonymize_partner(self.partner, dry_run=True)
        blocked_models = [item["model"] for item in report["blocked"]]
        self.assertIn("res.partner", blocked_models)

    def test_dry_run_does_not_modify_data(self):
        original = self.partner.name
        self.Engine.anonymize_partner(self.partner, dry_run=True)
        self.partner.invalidate_recordset()
        self.assertEqual(
            self.partner.name, original,
            "Une simulation ne doit rien écrire.",
        )
        self.assertFalse(self.partner.rgpd_anonymized)
