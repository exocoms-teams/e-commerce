# -*- coding: utf-8 -*-
"""Formulaire public de demande RGPD et endpoint de journalisation CMP."""

import logging
import secrets

from odoo import _, fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)

PUBLIC_REQUEST_TYPES = [
    ("access", "Accéder à mes données"),
    ("portability", "Récupérer mes données"),
    ("rectification", "Corriger mes données"),
    ("erasure", "Supprimer mes données"),
    ("restriction", "Limiter le traitement"),
    ("objection", "M'opposer au traitement"),
    ("withdraw", "Retirer mon consentement"),
    ("info", "Question sur mes données"),
]

# Anti-abus : nombre maximal de demandes acceptées par adresse IP et par heure.
RATE_LIMIT = 5


class RgpdPublic(http.Controller):

    def _enabled(self):
        return request.env.company.sudo().rgpd_public_form_enabled

    def _rate_limited(self):
        ip = request.httprequest.remote_addr
        if not ip:
            return False
        since = fields.Datetime.subtract(fields.Datetime.now(), hours=1)
        count = request.env["exocoms.rgpd.request"].sudo().search_count(
            [("source", "=", "public_form"), ("create_date", ">=", since)]
        )
        return count >= RATE_LIMIT * 20  # garde-fou global

    # ------------------------------------------------------------------
    @http.route(["/rgpd/demande"], type="http", auth="public", website=True, sitemap=True)
    def rgpd_public_form(self, **kwargs):
        if not self._enabled():
            return request.render("website.page_404")
        company = request.env.company.sudo()
        return request.render(
            "exocoms_rgpd.public_request_form",
            {
                "request_types": PUBLIC_REQUEST_TYPES,
                "company": company,
                "error": kwargs.get("error"),
                "values": {},
            },
        )

    @http.route(
        ["/rgpd/demande/envoi"], type="http", auth="public", website=True,
        methods=["POST"], csrf=True,
    )
    def rgpd_public_submit(self, **post):
        if not self._enabled():
            return request.render("website.page_404")
        company = request.env.company.sudo()
        errors = []
        name = (post.get("requester_name") or "").strip()
        email = (post.get("email") or "").strip()
        request_type = post.get("request_type")
        description = (post.get("description") or "").strip()[:5000]
        if not name:
            errors.append(_("Le nom est obligatoire."))
        if not email or "@" not in email:
            errors.append(_("Une adresse e-mail valide est obligatoire."))
        if request_type not in [code for code, _label in PUBLIC_REQUEST_TYPES]:
            errors.append(_("Sélectionnez la nature de votre demande."))
        if not post.get("consent_processing"):
            errors.append(
                _("Vous devez accepter le traitement de votre demande pour la soumettre.")
            )
        if post.get("website_url"):  # champ piège anti-robot
            errors.append(_("Requête invalide."))
        if self._rate_limited():
            errors.append(
                _("Trop de demandes reçues récemment. Merci de réessayer plus tard "
                  "ou d'écrire directement à %s.") % (company.rgpd_dpo_email or "")
            )
        if errors:
            return request.render(
                "exocoms_rgpd.public_request_form",
                {
                    "request_types": PUBLIC_REQUEST_TYPES,
                    "company": company,
                    "error": " ".join(errors),
                    "values": post,
                },
            )

        rgpd_request = request.env["exocoms.rgpd.request"].sudo().create(
            {
                "requester_name": name,
                "email": email,
                "phone": (post.get("phone") or "").strip()[:64],
                "request_type": request_type,
                "description": description,
                "source": "public_form",
                "is_third_party": bool(post.get("is_third_party")),
                "state": "identity",
            }
        )
        template = request.env.ref(
            "exocoms_rgpd.mail_template_rgpd_identity_check", raise_if_not_found=False
        )
        if template:
            template.sudo().send_mail(rgpd_request.id, force_send=True)
        _logger.info("RGPD: demande publique %s reçue.", rgpd_request.name)
        return request.render(
            "exocoms_rgpd.public_request_thanks",
            {"rgpd_request": rgpd_request, "company": company},
        )

    # ------------------------------------------------------------------
    @http.route(
        ["/rgpd/demande/confirmer/<string:token>"], type="http", auth="public", website=True
    )
    def rgpd_confirm(self, token, **kwargs):
        """Confirmation de l'adresse e-mail : vaut vérification d'identité de
        premier niveau pour les demandes ne portant pas sur des données
        sensibles."""
        rgpd_request = request.env["exocoms.rgpd.request"].sudo().search(
            [("access_token", "=", token)], limit=1
        )
        if not rgpd_request:
            return request.render("website.page_404")
        if not rgpd_request.identity_verified:
            rgpd_request.write(
                {
                    "identity_verified": True,
                    "identity_method": "email_token",
                    "identity_date": fields.Datetime.now(),
                    "identity_note": _("Adresse e-mail confirmée par jeton."),
                    "state": "progress",
                }
            )
            rgpd_request.message_post(
                body=_("Adresse e-mail confirmée par le demandeur depuis le lien "
                       "de vérification.")
            )
        return request.render(
            "exocoms_rgpd.public_request_confirmed",
            {"rgpd_request": rgpd_request, "company": request.env.company.sudo()},
        )

    # ------------------------------------------------------------------
    @http.route(
        ["/rgpd/consent/log"], type="jsonrpc", auth="public", csrf=False, methods=["POST"]
    )
    def rgpd_consent_log(self, purpose, email=None, granted=True, **kwargs):
        """Endpoint destiné aux CMP externes (Axeptio, tarteaucitron, Didomi).

        Attend l'en-tête ``X-RGPD-Key`` correspondant au paramètre système
        ``exocoms_rgpd.consent_api_key`` lorsque celui-ci est défini.
        """
        params = request.env["ir.config_parameter"].sudo()
        expected = params.get_param("exocoms_rgpd.consent_api_key")
        if expected:
            provided = request.httprequest.headers.get("X-RGPD-Key")
            if not provided or not secrets.compare_digest(provided, expected):
                return {"status": "error", "message": "unauthorized"}
        if not email:
            return {"status": "error", "message": "email required"}
        headers = request.httprequest.headers
        try:
            consent = request.env["exocoms.rgpd.consent"].sudo().register(
                purpose,
                email,
                granted=bool(granted),
                # Société du site appelant : en multi-société chaque entité est
                # un responsable de traitement distinct.
                company=request.env.company.sudo(),
                method=kwargs.get("method", "cookie_banner"),
                source_url=kwargs.get("source_url") or headers.get("Referer"),
                ip_address=request.httprequest.remote_addr,
                user_agent=headers.get("User-Agent"),
                external_ref=kwargs.get("external_ref"),
                consent_text=kwargs.get("consent_text"),
            )
        except Exception as exc:
            _logger.warning("RGPD: consentement externe rejeté (%s)", exc)
            return {"status": "error", "message": str(exc)}
        return {"status": "ok", "id": consent.id, "hash": consent.proof_hash}
