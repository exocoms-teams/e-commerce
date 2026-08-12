import json
from unittest.mock import patch

from odoo.tests.common import HttpCase


class TestTrackerCronLogModel(HttpCase):
    """WIN-83 : modele tracker.cron.log et journalisation best-effort."""

    def test_log_execution_creates_success_entry(self):
        self.env['tracker.cron.log'].log_execution(
            cron_name='test_script', status='success', message='ok',
        )
        log = self.env['tracker.cron.log'].search([('cron_name', '=', 'test_script')], limit=1)
        self.assertTrue(log)
        self.assertEqual(log.status, 'success')
        self.assertEqual(log.message, 'ok')

    def test_log_execution_creates_error_entry(self):
        self.env['tracker.cron.log'].log_execution(
            cron_name='test_script', status='error', message='connection error',
        )
        log = self.env['tracker.cron.log'].search([('cron_name', '=', 'test_script')], limit=1)
        self.assertEqual(log.status, 'error')
        self.assertIn('connection error', log.message)

    def test_log_execution_never_raises_on_internal_failure(self):
        """Contrainte du ticket : une erreur de journalisation ne doit
        jamais remonter au script appelant."""
        with patch.object(
            type(self.env['tracker.cron.log']), 'create',
            side_effect=Exception('db down'),
        ):
            try:
                self.env['tracker.cron.log'].log_execution(
                    cron_name='test_script', status='error', message='boom',
                )
            except Exception:
                self.fail("log_execution() ne doit jamais lever d'exception")


class TestEbayScanLogging(HttpCase):
    """Verifie que /dashboard/run_ebay_scan journalise bien le resultat,
    sans faire echouer le scan meme en cas d'erreur reseau simulee."""

    def setUp(self):
        super().setUp()
        admin = self.env.ref('base.user_admin')
        self.authenticate(admin.login, admin.login)

    def test_run_ebay_scan_logs_error_on_ingestion_failure(self):
        with patch(
            'odoo.addons.produits_tendance.controllers.main.run_ingestion_for_keyword',
            return_value={'status': 'error', 'message': "Échec de l'authentification eBay"},
        ):
            response = self.url_open(
                '/dashboard/run_ebay_scan',
                data=json.dumps({
                    'jsonrpc': '2.0', 'method': 'call', 'id': 1,
                    'params': {'keyword': 'test'},
                }),
                headers={'Content-Type': 'application/json'},
            )
        self.assertEqual(response.status_code, 200)

        log = self.env['tracker.cron.log'].search(
            [('cron_name', '=', 'ebay_ingestor')], order='id desc', limit=1,
        )
        self.assertTrue(log)
        self.assertEqual(log.status, 'error')
