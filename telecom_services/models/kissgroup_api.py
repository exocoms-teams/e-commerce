import logging

import requests

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://api.kissgroup.io'
REQUEST_TIMEOUT = 20  # seconds


class KissgroupApi(models.AbstractModel):
    """Thin client for the KISSGROUP Partner API.

    Authentication is a raw API key sent as a Bearer token. The key is read
    from the system parameter ``telecom_services.kissgroup_api_key`` and is
    never stored in the source tree.
    """

    _name = 'telecom.kissgroup.api'
    _description = 'KISSGROUP Partner API client'

    @api.model
    def _get_credentials(self):
        icp = self.env['ir.config_parameter'].sudo()
        api_key = icp.get_param('telecom_services.kissgroup_api_key')
        base_url = icp.get_param('telecom_services.kissgroup_base_url') or DEFAULT_BASE_URL
        return api_key, base_url.rstrip('/')

    @api.model
    def _request(self, method, path, params=None, payload=None):
        api_key, base_url = self._get_credentials()
        if not api_key:
            raise UserError(
                "Clé API KISSGROUP manquante. Renseignez le paramètre système "
                "'telecom_services.kissgroup_api_key' (Configuration > Technique > "
                "Paramètres système)."
            )
        headers = {
            'Authorization': 'Bearer %s' % api_key,
            'Accept': 'application/json',
        }
        try:
            response = requests.request(
                method, base_url + path,
                headers=headers, params=params, json=payload,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as err:
            # Never log headers/key.
            _logger.error("KISSGROUP %s %s failed: %s", method, path, err)
            raise UserError("Connexion à l'API KISSGROUP impossible : %s" % err)

        if response.status_code >= 400:
            _logger.error(
                "KISSGROUP %s %s -> HTTP %s: %s",
                method, path, response.status_code, response.text[:500],
            )
            raise UserError(
                "L'API KISSGROUP a renvoyé une erreur HTTP %s." % response.status_code
            )

        if not response.content:
            return None
        return response.json()

    @api.model
    def whoami(self):
        """Auth smoke-test: GET /v1/me. Returns partner + key scope info."""
        return self._request('GET', '/v1/me')

    @api.model
    def get_mobile_plans(self, provider=None):
        """Return the full KissMobile plan catalogue (list of plan dicts)."""
        params = {'provider': provider} if provider else None
        return self._request('GET', '/v1/kissmobile/plans', params=params) or []

    @api.model
    def get_sim_packs(self):
        """Return the orderable KissMobile SIM packs (list of pack dicts)."""
        return self._request('GET', '/v1/kissmobile/sim-packs') or []
