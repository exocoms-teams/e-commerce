# -*- coding: utf-8 -*-
"""Espace « Mes données personnelles » du portail client."""

import base64
import json
import logging

from odoo import _, fields, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)

REQUEST_TYPES_PORTAL = [
    ("access", "Obtenir une copie de mes données (droit d'accès)"),
    ("portability", "Récupérer mes données dans un format réutilisable"),
    ("rectification", "Corriger des données inexactes"),
    ("erasure", "Supprimer mes données"),
    ("restriction", "Limiter le traitement de mes données"),
    ("objection", "M'opposer à un traitement"),
    ("withdraw", "Retirer un consentement"),
    ("info", "Poser une question sur mes données"),
]


class RgpdPortal(CustomerPortal):

    # ------------------------------------------------------------------
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "rgpd_count" in counters:
            partner = request.env.user.partner_id
            values["rgpd_count"] = request.env["exocoms.rgpd.request"].sudo().search_count(
                [("partner_id", "=", partner.id)]
            )
        return values

    def _rgpd_enabled(self):
        return request.env.company.sudo().rgpd_portal_enabled

    def _rgpd_values(self):
        partner = request.env.user.partner_id
        company = request.env.company.sudo()
        Consent = request.env["exocoms.rgpd.consent"].sudo()
        purposes = request.env["exocoms.rgpd.consent.purpose"]._applicable(
            company=company, extra_domain=[("portal_visible", "=", True)]
        )
        current = Consent.get_current_state(partner.email, partner, company=company)
        consent_lines = []
        for purpose in purposes:
            consent = current.get(purpose.code)
            consent_lines.append(
                {
                    "purpose": purpose,
                    "granted": bool(consent and consent.state == "granted") or purpose.essential,
                    "date": consent.date_event if consent else False,
                    "state": consent.state if consent else "none",
                }
            )
        requests = request.env["exocoms.rgpd.request"].sudo().search(
            [("partner_id", "=", partner.id)], order="date_request desc", limit=20
        )
        return {
            "partner": partner,
            "company": company,
            "consent_lines": consent_lines,
            "requests": requests,
            "request_types": REQUEST_TYPES_PORTAL,
            "page_name": "rgpd_privacy",
        }

    # ------------------------------------------------------------------
    @http.route(["/my/privacy"], type="http", auth="user", website=True)
    def portal_privacy(self, **kwargs):
        if not self._rgpd_enabled():
            return request.redirect("/my")
        values = self._rgpd_values()
        values.update(
            {
                "message": kwargs.get("message"),
                "error": kwargs.get("error"),
            }
        )
        return request.render("exocoms_rgpd.portal_privacy", values)

    @http.route(["/my/privacy/data"], type="http", auth="user", website=True)
    def portal_privacy_data(self, **kwargs):
        """Aperçu détaillé des données détenues."""
        if not self._rgpd_enabled():
            return request.redirect("/my")
        partner = request.env.user.partner_id
        data = request.env["exocoms.rgpd.engine"].sudo().collect_personal_data(partner)
        return request.render(
            "exocoms_rgpd.portal_privacy_data",
            {"data": data, "partner": partner, "page_name": "rgpd_privacy"},
        )

    @http.route(["/my/privacy/download"], type="http", auth="user", website=True)
    def portal_privacy_download(self, **kwargs):
        if not self._rgpd_enabled():
            return request.redirect("/my")
        partner = request.env.user.partner_id
        data = request.env["exocoms.rgpd.engine"].sudo().collect_personal_data(partner)
        payload = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        filename = "mes-donnees-personnelles-%s.json" % partner.id
        return request.make_response(
            payload.encode("utf-8"),
            headers=[
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Disposition", 'attachment; filename="%s"' % filename),
                ("Cache-Control", "no-store"),
            ],
        )

    @http.route(["/my/privacy/pdf"], type="http", auth="user", website=True)
    def portal_privacy_pdf(self, **kwargs):
        if not self._rgpd_enabled():
            return request.redirect("/my")
        partner = request.env.user.partner_id
        pdf, _content_type = (
            request.env["ir.actions.report"]
            .sudo()
            ._render_qweb_pdf("exocoms_rgpd.action_report_rgpd_partner_export", [partner.id])
        )
        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(pdf)),
                (
                    "Content-Disposition",
                    'attachment; filename="mes-donnees-personnelles.pdf"',
                ),
            ],
        )

    # ------------------------------------------------------------------
    @http.route(
        ["/my/privacy/consent"], type="http", auth="user", website=True,
        methods=["POST"], csrf=True,
    )
    def portal_privacy_consent(self, **post):
        if not self._rgpd_enabled():
            return request.redirect("/my")
        partner = request.env.user.partner_id
        Consent = request.env["exocoms.rgpd.consent"].sudo()
        company = request.env.company.sudo()
        purposes = request.env["exocoms.rgpd.consent.purpose"]._applicable(
            company=company,
            extra_domain=[("portal_visible", "=", True), ("essential", "=", False)],
        )
        current = Consent.get_current_state(partner.email, partner, company=company)
        headers = request.httprequest.headers
        meta = {
            "method": "portal",
            "source_url": request.httprequest.url,
            "ip_address": request.httprequest.remote_addr,
            "user_agent": headers.get("User-Agent"),
            "company": company,
        }
        changed = 0
        for purpose in purposes:
            wanted = post.get("consent_%s" % purpose.code) in ("on", "1", "true")
            existing = current.get(purpose.code)
            is_granted = bool(existing and existing.state == "granted")
            if wanted == is_granted:
                continue
            if wanted:
                Consent.register(
                    purpose.code, partner.email, granted=True, partner=partner, **meta
                )
            else:
                Consent.withdraw(purpose.code, partner.email, partner=partner, **meta)
            changed += 1
        return request.redirect(
            "/my/privacy?message=%s" % ("saved" if changed else "nochange")
        )

    # ------------------------------------------------------------------
    @http.route(
        ["/my/privacy/request"], type="http", auth="user", website=True,
        methods=["POST"], csrf=True,
    )
    def portal_privacy_request(self, **post):
        if not self._rgpd_enabled():
            return request.redirect("/my")
        partner = request.env.user.partner_id
        request_type = post.get("request_type")
        valid = [code for code, _label in REQUEST_TYPES_PORTAL]
        if request_type not in valid:
            return request.redirect("/my/privacy?error=type")
        description = (post.get("description") or "").strip()[:5000]
        rgpd_request = request.env["exocoms.rgpd.request"].sudo().create(
            {
                "partner_id": partner.id,
                "requester_name": partner.name,
                "email": partner.email,
                "phone": partner.phone,
                "request_type": request_type,
                "description": description,
                "source": "portal",
                "identity_verified": True,
                "identity_method": "portal",
                "identity_date": fields.Datetime.now(),
                "state": "progress",
            }
        )
        _logger.info("RGPD: demande portail %s créée par %s", rgpd_request.name, partner.id)
        return request.redirect("/my/privacy?message=request")
