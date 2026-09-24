# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

import base64
import json
import logging
import time
from datetime import timedelta
from urllib.parse import urlparse

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import urls

from odoo.addons.exocoms_revolut_reconciliation import const

_logger = logging.getLogger(__name__)

TIMEOUT = 60


class RevolutBusinessConnection(models.Model):
    _name = 'revolut.business.connection'
    _description = "Connexion Revolut Business"
    _order = 'company_id, name'

    name = fields.Char(required=True, default="Revolut Business")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company, ondelete='cascade'
    )
    is_live = fields.Boolean(
        string="Production",
        help="Décoché, la connexion utilise le bac à sable "
             "(https://sandbox-b2b.revolut.com).",
    )

    # --- Identifiants fournis par Revolut ---
    client_id = fields.Char(
        string="Client ID",
        help="Identifiant émis par Revolut lors de l'enregistrement du certificat API.",
        groups='base.group_system',
    )
    private_key = fields.Text(
        string="Clé privée (PEM)",
        help="Clé privée RSA dont la moitié publique a été déposée dans Revolut Business. "
             "Sert à signer le JWT d'assertion client.",
        groups='base.group_system',
    )
    redirect_uri = fields.Char(
        string="URI de redirection OAuth",
        help="URI de redirection déclarée dans Revolut Business. Son domaine sert d'émetteur "
             "(claim `iss`) du JWT.",
        groups='base.group_system',
    )

    # --- Jetons ---
    refresh_token = fields.Char(copy=False, groups='base.group_system')
    refresh_token_expiry = fields.Datetime(
        string="Expiration du jeton de rafraîchissement", readonly=True, copy=False
    )
    access_token = fields.Char(copy=False, groups='base.group_system')
    access_token_expiry = fields.Datetime(readonly=True, copy=False)

    state = fields.Selection(
        [('draft', "À configurer"), ('connected', "Connectée"), ('expired', "À reconnecter")],
        compute='_compute_state',
        store=True,
    )
    journal_ids = fields.One2many('account.journal', 'revolut_connection_id')
    journal_count = fields.Integer(compute='_compute_journal_count')

    _name_company_uniq = models.Constraint(
        'unique(company_id, name)',
        "Le nom d'une connexion Revolut doit être unique par société.",
    )

    # === COMPUTE === #

    @api.depends('refresh_token', 'refresh_token_expiry')
    def _compute_state(self):
        now = fields.Datetime.now()
        for connection in self:
            if not connection.sudo().refresh_token:
                connection.state = 'draft'
            elif connection.refresh_token_expiry and connection.refresh_token_expiry < now:
                connection.state = 'expired'
            else:
                connection.state = 'connected'

    @api.depends('journal_ids')
    def _compute_journal_count(self):
        for connection in self:
            connection.journal_count = len(connection.journal_ids)

    # === AUTHENTIFICATION === #

    def _get_base_url(self):
        self.ensure_one()
        return const.API_BASE_URL_LIVE if self.is_live else const.API_BASE_URL_SANDBOX

    def _build_client_assertion(self):
        """Build the RS256-signed JWT that authenticates every token exchange.

        Signed with `cryptography` rather than a JWT library: `cryptography` is already a hard
        dependency of Odoo, so the module installs without touching requirements.txt.

        :return: The encoded JWT.
        :rtype: str
        """
        self.ensure_one()

        connection = self.sudo()
        if not connection.private_key or not connection.client_id or not connection.redirect_uri:
            raise UserError(_(
                "Renseignez le client ID, la clé privée et l'URI de redirection avant de vous "
                "connecter à Revolut."
            ))

        issuer = urlparse(connection.redirect_uri).hostname
        if not issuer:
            raise UserError(_(
                "L'URI de redirection OAuth doit être une URL complète, par exemple "
                "https://exemple.fr/revolut/business/callback."
            ))

        header = {'alg': 'RS256', 'typ': 'JWT'}
        payload = {
            'iss': issuer,
            'sub': connection.client_id,
            'aud': const.JWT_AUDIENCE,
            'exp': int(time.time()) + const.JWT_LIFETIME_SECONDS,
        }
        signing_input = b'.'.join(
            self._b64url(json.dumps(part, separators=(',', ':')).encode())
            for part in (header, payload)
        )
        signature = self._sign_rs256(signing_input, connection.private_key)
        return (signing_input + b'.' + self._b64url(signature)).decode()

    @staticmethod
    def _b64url(raw):
        return base64.urlsafe_b64encode(raw).rstrip(b'=')

    @staticmethod
    def _sign_rs256(message, private_key_pem):
        """Sign a message with an RSA private key using PKCS#1 v1.5 and SHA-256."""
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding, rsa

        try:
            key = serialization.load_pem_private_key(
                private_key_pem.strip().encode(), password=None
            )
        except Exception as error:
            raise UserError(
                _("La clé privée n'est pas une clé PEM valide : %s", error)
            ) from error
        if not isinstance(key, rsa.RSAPrivateKey):
            raise UserError(_("Revolut exige une clé RSA pour signer le JWT d'assertion."))
        return key.sign(message, padding.PKCS1v15(), hashes.SHA256())

    def _exchange_token(self, payload):
        """Call the token endpoint and store the returned credentials.

        :param dict payload: The form-encoded body, without the client assertion.
        :return: None
        """
        self.ensure_one()

        connection = self.sudo()
        body = {
            **payload,
            'client_id': connection.client_id,
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': self._build_client_assertion(),
        }
        url = urls.urljoin(self._get_base_url(), 'auth/token')
        try:
            response = requests.post(
                url,
                data=body,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            content = response.json()
        except requests.exceptions.RequestException as error:
            _logger.exception("Revolut token exchange failed.")
            raise UserError(
                _("Revolut a refusé l'échange de jeton : %s", error)
            ) from error

        values = {
            'access_token': content.get('access_token'),
            'access_token_expiry': fields.Datetime.now() + timedelta(
                seconds=max(
                    int(content.get('expires_in', 0))
                    - const.ACCESS_TOKEN_SAFETY_MARGIN_SECONDS,
                    0,
                )
            ),
        }
        # A refresh token is only returned by the authorization_code grant.
        if content.get('refresh_token'):
            values['refresh_token'] = content['refresh_token']
            values['refresh_token_expiry'] = fields.Datetime.now() + timedelta(days=90)
        connection.write(values)

    def action_exchange_authorization_code(self, code):
        """Exchange the one-off authorization code for a refresh token."""
        self.ensure_one()
        self._exchange_token({'grant_type': 'authorization_code', 'code': code})

    def _get_access_token(self):
        """Return a valid access token, refreshing it when needed.

        :return: The access token.
        :rtype: str
        """
        self.ensure_one()

        connection = self.sudo()
        if not connection.refresh_token:
            raise UserError(_(
                "La connexion « %s » n'est pas encore autorisée. Lancez l'autorisation depuis "
                "Revolut Business pour obtenir un jeton de rafraîchissement.",
                self.display_name,
            ))
        if (
            not connection.access_token
            or not connection.access_token_expiry
            or connection.access_token_expiry <= fields.Datetime.now()
        ):
            self._exchange_token({
                'grant_type': 'refresh_token',
                'refresh_token': connection.refresh_token,
            })
        return connection.access_token

    # === APPELS API === #

    def _api_get(self, endpoint, params=None):
        """Perform an authenticated GET request against the Business API.

        :param str endpoint: The endpoint, relative to the API base URL.
        :param dict params: The query string parameters.
        :return: The parsed response.
        :rtype: dict | list
        """
        self.ensure_one()

        url = urls.urljoin(self._get_base_url(), endpoint.strip('/'))
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self._get_access_token()}',
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            _logger.exception("Revolut Business API request to %s failed.", endpoint)
            raise UserError(
                _("Appel à la Business API de Revolut en échec (%(endpoint)s) : %(error)s",
                  endpoint=endpoint, error=error)
            ) from error
        return response.json() if response.content else {}

    def action_test_connection(self):
        """Check the credentials by listing the Revolut accounts."""
        self.ensure_one()

        accounts = self._api_get('accounts')
        names = ", ".join(
            f"{a.get('name') or a.get('id')} ({a.get('currency')})" for a in accounts
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _("Connexion établie. Comptes disponibles : %s", names or "aucun"),
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_view_journals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Journaux liés"),
            'res_model': 'account.journal',
            'view_mode': 'list,form',
            'domain': [('revolut_connection_id', '=', self.id)],
        }

    # === CRON === #

    @api.model
    def _cron_sync_revolut_transactions(self):
        """Synchronise every journal attached to an authorised connection."""
        journals = self.env['account.journal'].search([
            ('revolut_sync_enabled', '=', True),
            ('revolut_connection_id.state', '=', 'connected'),
        ])
        for journal in journals:
            try:
                with self.env.cr.savepoint():
                    journal.action_revolut_sync()
            except Exception:  # noqa: BLE001 - one journal must not break the whole cron.
                _logger.exception(
                    "Revolut synchronisation failed for journal %s.", journal.display_name
                )
