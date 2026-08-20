# -*- coding: utf-8 -*-
"""Workflow des demandes d'exercice des droits (art. 12 et 15 à 22)."""
import logging

_logger = logging.getLogger(__name__)
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged


from .common import RgpdCommon


@tagged("post_install", "-at_install", "rgpd")
class TestRequestWorkflow(RgpdCommon):

    def _request(self, **vals):
        base = {
            "requester_name": "Jean Testeur",
            "email": self.partner.email,
            "request_type": "access",
        }
        base.update(vals)
        return self.Request.with_company(self.company_a).create(base)

    def test_deadline_is_one_month(self):
        request = self._request()
        expected = fields.Datetime.to_datetime(request.date_request).date() \
            + relativedelta(months=1)
        self.assertEqual(request.date_deadline, expected)

    def test_extension_adds_two_months(self):
        request = self._request()
        original = request.date_deadline
        request.extension_reason = "Demande complexe portant sur huit ans d'archives."
        request.action_extend()
        self.assertTrue(request.extension_granted)
        self.assertEqual(request.date_deadline, original + relativedelta(months=2))
        self.assertEqual(request.state, "extended")

    def test_cannot_close_without_identity_verification(self):
        """Article 12.6 : aucune donnée ne sort sans vérification d'identité.

        C'est le garde-fou qui empêche de transformer le module en canal
        d'exfiltration : il suffirait d'écrire au DPO en usurpant une adresse.
        """
        request = self._request()
        self.assertFalse(request.identity_verified)
        try:
            request.action_close()
        except (UserError, ValidationError):
            pass
        else:
            self.fail("La fermeture aurait dû lever une exception")

    def test_close_succeeds_after_identity_verification(self):
        request = self._request()
        request.action_confirm_identity()
        self.assertTrue(request.identity_verified)
        request.response_note="OK"
        request.action_done()
        self.assertEqual(request.state, "done")
        self.assertTrue(request.date_response)

    def test_access_token_is_generated_and_unique(self):
        first = self._request()
        second = self._request(email="autre@exemple.fr")
        self.assertTrue(first.access_token)
        self.assertNotEqual(first.access_token, second.access_token)

    def test_partner_is_matched_from_email(self):
        request = self._request()
        self.assertEqual(request.partner_id, self.partner)

    def test_late_flag_and_search(self):
        request = self._request()
        request.date_request = (
            fields.Datetime.now() - relativedelta(months=3)
        )
        self.assertTrue(request.is_late)
        domain = request._search_is_late("=", True)
        self.assertIn(request, self.Request.search(domain))

    def test_export_generation_produces_json(self):
        request = self._request(request_type="portability")
        request.action_confirm_identity()
        request.action_generate_export()
        self.assertTrue(request.export_data)
        self.assertTrue(request.export_filename.endswith(".json"))

    def test_collect_personal_data_returns_subject_identity(self):
        data = self.Engine.collect_personal_data(self.partner)
        self.assertEqual(data["meta"]["subject"]["id"], self.partner.id)
        self.assertIn("sections", data)
