# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

import hashlib
import hmac
import time

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import urls

from odoo.addons.payment.logging import get_payment_logger
from odoo.addons.exocoms_payment_revolut import const

_logger = get_payment_logger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('revolut', "Revolut Business")],
        ondelete={'revolut': 'set default'},
    )
    revolut_secret_key = fields.Char(
        string="Clé secrète Revolut",
        help="Clé secrète de la Merchant API (sk_...). Utilisez la clé Sandbox tant que le "
             "fournisseur n'est pas en production.",
        required_if_provider='revolut',
        copy=False,
        groups='base.group_system',
    )
    revolut_public_key = fields.Char(
        string="Clé publique Revolut",
        help="Clé publique de la Merchant API (pk_...). Non requise pour le flux par redirection.",
        copy=False,
        groups='base.group_system',
    )
    revolut_webhook_secret = fields.Char(
        string="Secret de signature du webhook",
        help="Secret de signature (wsk_...) renvoyé par Revolut à la création du webhook. "
             "Utilisez le bouton « Créer le webhook » pour le renseigner automatiquement.",
        copy=False,
        groups='base.group_system',
    )
    revolut_webhook_id = fields.Char(
        string="Identifiant du webhook Revolut",
        copy=False,
        groups='base.group_system',
    )

    # === COMPUTE METHODS === #

    def _compute_feature_support_fields(self):
        """Override of `payment` to enable additional features."""
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'revolut').update({
            'support_manual_capture': 'partial',
            'support_refund': 'partial',
        })

    def _get_supported_currencies(self):
        """Override of `payment` to return the supported currencies."""
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'revolut':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    # === CRUD METHODS === #

    def _get_default_payment_method_codes(self):
        """Override of `payment` to return the default payment method codes."""
        self.ensure_one()

        if self.code != 'revolut':
            return super()._get_default_payment_method_codes()
        return const.DEFAULT_PAYMENT_METHOD_CODES

    def _get_removal_values(self):
        """Override of `payment` to clear the Revolut credentials on uninstall."""
        return {
            **super()._get_removal_values(),
            'revolut_secret_key': False,
            'revolut_public_key': False,
            'revolut_webhook_secret': False,
            'revolut_webhook_id': False,
        }

    # === REQUEST HELPERS === #

    def _build_request_url(self, endpoint, **kwargs):
        """Override of `payment` to build the request URL."""
        if self.code != 'revolut':
            return super()._build_request_url(endpoint, **kwargs)

        base_url = const.API_BASE_URL_LIVE if self.is_live else const.API_BASE_URL_SANDBOX
        return urls.urljoin(base_url, endpoint.strip('/'))

    def _build_request_headers(self, method, endpoint, payload, idempotency_key=None, **kwargs):
        """Override of `payment` to build the request headers."""
        if self.code != 'revolut':
            return super()._build_request_headers(
                method, endpoint, payload, idempotency_key=idempotency_key, **kwargs
            )

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.revolut_secret_key}',
            'Content-Type': 'application/json',
            'Revolut-Api-Version': const.API_VERSION,
        }
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        return headers

    def _parse_response_error(self, response):
        """Override of `payment` to parse the error message."""
        if self.code != 'revolut':
            return super()._parse_response_error(response)

        try:
            content = response.json()
        except ValueError:
            return response.text
        if isinstance(content, dict):
            return content.get('message') or content.get('error') or response.text
        return response.text

    def _parse_response_content(self, response, **kwargs):
        """Override of `payment` to tolerate empty bodies (e.g. 204 No Content)."""
        if self.code != 'revolut':
            return super()._parse_response_content(response, **kwargs)

        if not response.content:
            return {}
        return response.json()

    # === WEBHOOK MANAGEMENT === #

    def action_revolut_create_webhook(self):
        """Register the notification webhook on Revolut and store its signing secret.

        :return: A client action displaying the outcome.
        :rtype: dict
        """
        self.ensure_one()

        if self.code != 'revolut':
            return

        webhook_url = urls.urljoin(self.get_base_url(), '/payment/revolut/webhook')
        if webhook_url.startswith('http://'):
            raise UserError(_(
                "Revolut n'accepte que des URL de webhook en HTTPS. URL calculée : %s", webhook_url
            ))

        payload = {'url': webhook_url, 'events': const.WEBHOOK_EVENTS}
        webhook = self._revolut_call_webhook_endpoint('POST', 'webhooks', json=payload)

        self.write({
            'revolut_webhook_id': webhook.get('id'),
            'revolut_webhook_secret': webhook.get('signing_secret'),
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _("Webhook Revolut enregistré sur %s.", webhook_url),
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_revolut_delete_webhook(self):
        """Delete the previously registered webhook on Revolut."""
        self.ensure_one()

        if self.code != 'revolut' or not self.revolut_webhook_id:
            return

        self._revolut_call_webhook_endpoint('DELETE', f'webhooks/{self.revolut_webhook_id}')
        self.write({'revolut_webhook_id': False, 'revolut_webhook_secret': False})

    def _revolut_call_webhook_endpoint(self, method, endpoint, **kwargs):
        """Call a webhook endpoint, falling back to the legacy `1.0` path if needed.

        :param str method: The HTTP method of the request.
        :param str endpoint: The webhook endpoint, without the leading API path.
        :return: The parsed response content.
        :rtype: dict
        """
        self.ensure_one()

        try:
            return self._send_api_request(method, endpoint, **kwargs)
        except ValidationError:
            _logger.info(
                "Revolut webhook endpoint %s unavailable, retrying on the legacy path.", endpoint
            )
            return self._send_api_request(method, f'1.0/{endpoint}', **kwargs)

    def _revolut_verify_webhook_signature(self, raw_body, timestamp, signature_header):
        """Check the authenticity of a webhook notification.

        :param str raw_body: The raw, unparsed body of the notification.
        :param str timestamp: The value of the `Revolut-Request-Timestamp` header.
        :param str signature_header: The value of the `Revolut-Signature` header.
        :return: Whether the notification is authentic.
        :rtype: bool
        """
        self.ensure_one()

        if not self.revolut_webhook_secret:
            _logger.warning(
                "Ignoring Revolut webhook: no signing secret configured on provider %s.", self.id
            )
            return False
        if not raw_body or not timestamp or not signature_header:
            return False

        # Reject replayed notifications.
        try:
            timestamp_ms = int(timestamp)
        except (TypeError, ValueError):
            return False
        if abs(int(time.time() * 1000) - timestamp_ms) > const.WEBHOOK_TIMESTAMP_TOLERANCE_MS:
            _logger.warning("Ignoring Revolut webhook: timestamp outside of tolerance.")
            return False

        expected = 'v1=' + hmac.new(
            self.revolut_webhook_secret.encode(),
            f'v1.{timestamp}.{raw_body}'.encode(),
            hashlib.sha256,
        ).hexdigest()

        # During a secret rotation, several signatures may be sent; any match is valid.
        return any(
            hmac.compare_digest(candidate.strip(), expected)
            for candidate in signature_header.split(',')
        )
