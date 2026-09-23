# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

import logging

from odoo import _, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RevolutBusinessController(http.Controller):
    _callback_url = '/revolut/business/callback'

    @http.route(_callback_url, type='http', auth='user', methods=['GET'], csrf=False)
    def revolut_business_callback(self, code=None, connection_id=None, **kwargs):
        """Capture the one-off authorization code returned by Revolut Business.

        The route is `auth='user'`: only a signed-in Odoo user completing the setup can turn the
        code into a refresh token, and access rights on the connection still apply.

        :param str code: The authorization code issued by Revolut.
        :param str connection_id: The connection being authorised, carried in the redirect URI.
        """
        if not code:
            return self._error_page(_(
                "Revolut n'a pas renvoyé de code d'autorisation. Relancez l'activation de "
                "l'accès API depuis l'application Revolut Business."
            ))

        connection = request.env['revolut.business.connection'].browse(
            int(connection_id) if connection_id else False
        ).exists()
        if not connection:
            connection = request.env['revolut.business.connection'].search(
                [('company_id', 'in', request.env.companies.ids)], limit=1
            )
        if not connection:
            return self._error_page(
                _("Aucune connexion Revolut Business n'est configurée dans Odoo.")
            )

        connection.check_access('write')
        connection.action_exchange_authorization_code(code)
        _logger.info("Revolut Business connection %s authorised.", connection.id)

        return request.redirect(f'/odoo/revolut.business.connection/{connection.id}')

    @staticmethod
    def _error_page(message):
        """Return a minimal HTML page describing why the authorisation failed."""
        body = (
            "<html><head><meta charset='utf-8'/>"
            "<title>Autorisation Revolut</title></head>"
            f"<body><h1>Autorisation Revolut</h1><p>{message}</p></body></html>"
        )
        return request.make_response(
            body, headers=[('Content-Type', 'text/html; charset=utf-8')]
        )
