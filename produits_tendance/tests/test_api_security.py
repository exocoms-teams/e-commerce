import json

from odoo.tests.common import HttpCase
from odoo.tools import mute_logger


@mute_logger('odoo.sql_db', 'odoo.http')
class TestIngestApiKeySecurity(HttpCase):
    """Epic 1.D - Support et Infrastructure : "Sécuriser l'endpoint (clé
    API)". Le contrôle d'accès de /api/trend/ingest (TrendIngestController
    .check_api_key) n'était couvert par aucun test - seuls des appels avec
    une clé déjà valide étaient exercés ailleurs (test_ad_ingestion.py)."""

    def setUp(self):
        super().setUp()
        self.valid_key = 'test-security-valid-key'
        self.env['ir.config_parameter'].sudo().set_param('winners.api_key', self.valid_key)

    def _ingest(self, api_key, data_type='score', data=None):
        response = self.url_open(
            '/api/trend/ingest',
            data=json.dumps({'api_key': api_key, 'type': data_type, 'data': data or {}}),
            headers={'Content-Type': 'application/json'},
        )
        return response.status_code, json.loads(response.text)

    def test_missing_api_key_rejected(self):
        status, payload = self._ingest(api_key=None)
        self.assertEqual(status, 401)
        self.assertEqual(payload['code'], 'missing_field')

    def test_wrong_api_key_rejected(self):
        status, payload = self._ingest(api_key='not-the-right-key')
        self.assertEqual(status, 403)
        self.assertEqual(payload['code'], 'invalid_api_key')

    def test_key_that_is_a_prefix_of_the_real_one_is_rejected(self):
        """Cas limite pertinent pour une comparaison en temps constant
        (hmac.compare_digest) : un préfixe correct ne doit jamais être
        accepté ni traité différemment d'une clé totalement fausse."""
        status, payload = self._ingest(api_key=self.valid_key[:5])
        self.assertEqual(status, 403)
        self.assertEqual(payload['code'], 'invalid_api_key')

    def test_valid_api_key_accepted(self):
        status, payload = self._ingest(
            api_key=self.valid_key,
            data_type='product',
            data={
                'name': 'Produit sécurité (test)',
                'product_ref': 'TEST-SECURITY-0001',
                'category': 'Sécurité',
                'country': 'MA',
                'source': 'api',
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload['status'], 'success')

    def test_no_api_key_configured_rejects_every_call(self):
        """Si winners.api_key n'est pas configuré du tout (get_param
        renvoie False), aucune clé - même vide - ne doit jamais être
        acceptée."""
        self.env['ir.config_parameter'].sudo().search([
            ('key', '=', 'winners.api_key'),
        ]).unlink()
        status, payload = self._ingest(api_key='anything')
        self.assertEqual(status, 403)
        self.assertEqual(payload['code'], 'invalid_api_key')
