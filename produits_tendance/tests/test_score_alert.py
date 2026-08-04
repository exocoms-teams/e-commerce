from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase


def _make_product(env, ref_suffix):
    return env['trend.product'].create({
        'name': 'Produit Alerte Test',
        'product_ref': f'TEST-ALERT-{ref_suffix}',
        'country': 'MA',
        'source': 'api',
    })


class TestScoreAlerts(TransactionCase):
    """WIN-67 : vérifie que le dépassement de seuil génère un mail.mail pour
    les abonnés Standard et une entrée trend.webhook.queue pour les Pro.

    Seuil et URL de webhook fixés une fois en setUpClass et JAMAIS modifiés
    en cours de test : ir.config_parameter est mis en cache (ormcache), et
    modifier un paramètre puis le relire dans la même transaction ne reflète
    pas toujours le changement de façon fiable (constaté : un set_param('')
    suivi d'un get_param() dans le même test renvoyait encore l'ancienne
    valeur). Les scénarios "pas configuré" sont donc dans des classes à part
    (ci-dessous) qui ne définissent jamais le paramètre concerné."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].sudo().set_param(
            'produits_tendance.score_alert_threshold', '50'
        )
        cls.env['ir.config_parameter'].sudo().set_param(
            'produits_tendance.webhook_url', 'https://hooks.example.com/webhook-test'
        )

        cls.standard_group = cls.env.ref('produits_tendance.group_trend_standard')
        cls.pro_group = cls.env.ref('produits_tendance.group_trend_pro')

        cls.standard_user = cls.env['res.users'].create({
            'name': 'Standard Test WIN-67',
            'login': 'standard.win67@example.com',
            'email': 'standard.win67@example.com',
            'group_ids': [(4, cls.standard_group.id)],
        })
        cls.pro_user = cls.env['res.users'].create({
            'name': 'Pro Test WIN-67',
            'login': 'pro.win67@example.com',
            'email': 'pro.win67@example.com',
            'group_ids': [(4, cls.pro_group.id)],
        })

    def setUp(self):
        super().setUp()
        # Un produit par test : évite qu'un test qui vérifie une absence
        # d'alerte retrouve l'entrée créée par un autre test du même produit.
        self.product = _make_product(self.env, self.id())

    def test_score_above_threshold_emails_standard_users_only(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 75.0,
        })

        recipients = self.env['mail.mail'].search([
            ('email_to', '=', self.standard_user.email),
        ])
        self.assertTrue(recipients, "un mail.mail doit être créé pour l'utilisateur Standard")

        pro_recipients = self.env['mail.mail'].search([
            ('email_to', '=', self.pro_user.email),
        ])
        self.assertFalse(pro_recipients, "l'utilisateur Pro ne doit pas recevoir d'email (il reçoit le webhook)")

    def test_score_above_threshold_queues_webhook(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 60.0,
        })

        queued = self.env['trend.webhook.queue'].search([('product_id', '=', self.product.id)])
        self.assertEqual(len(queued), 1)
        self.assertEqual(queued.state, 'pending')
        self.assertEqual(queued.url, 'https://hooks.example.com/webhook-test')
        self.assertIn('60.0', queued.payload)

    def test_score_below_threshold_does_not_alert(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 10.0,
        })

        self.assertFalse(self.env['mail.mail'].search([('email_to', '=', self.standard_user.email)]))
        self.assertFalse(self.env['trend.webhook.queue'].search([('product_id', '=', self.product.id)]))


class TestScoreAlertsNoThreshold(TransactionCase):
    """WIN-67 : aucune alerte ne doit être déclenchée si le seuil n'est pas
    configuré. `score_alert_threshold` n'est délibérément jamais défini ici."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].sudo().set_param(
            'produits_tendance.webhook_url', 'https://hooks.example.com/webhook-test'
        )
        cls.product = _make_product(cls.env, 'no-threshold')

    def test_no_threshold_configured_does_not_alert(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 999.0,
        })

        self.assertFalse(self.env['trend.webhook.queue'].search([('product_id', '=', self.product.id)]))


class TestScoreAlertsNoWebhookUrl(TransactionCase):
    """WIN-67 : le seuil peut être dépassé, mais sans URL de webhook
    configurée, rien ne doit être mis en file d'attente. `webhook_url`
    n'est délibérément jamais définie ici."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].sudo().set_param(
            'produits_tendance.score_alert_threshold', '50'
        )
        cls.product = _make_product(cls.env, 'no-webhook-url')

    def test_no_webhook_url_configured_does_not_queue(self):
        self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_score': 60.0,
        })

        self.assertFalse(self.env['trend.webhook.queue'].search([('product_id', '=', self.product.id)]))


class TestWebhookQueueCron(TransactionCase):
    """WIN-67 : vérifie que le traitement de la file d'attente envoie bien
    la requête HTTP (mockée) hors du thread de création du score."""

    def test_cron_sends_pending_webhook(self):
        job = self.env['trend.webhook.queue'].create({
            'url': 'https://hooks.example.com/webhook-test',
            'payload': '{"text": "test"}',
        })

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        with patch('odoo.addons.produits_tendance.models.trend_webhook_queue.requests.post',
                   return_value=mock_response) as mock_post:
            self.env['trend.webhook.queue']._cron_process_pending()

        mock_post.assert_called_once()
        self.assertEqual(job.state, 'sent')

    def test_cron_marks_failed_on_error(self):
        job = self.env['trend.webhook.queue'].create({
            'url': 'https://hooks.example.com/webhook-test',
            'payload': '{"text": "test"}',
        })

        with patch('odoo.addons.produits_tendance.models.trend_webhook_queue.requests.post',
                   side_effect=Exception("connection error")):
            self.env['trend.webhook.queue']._cron_process_pending()

        self.assertEqual(job.state, 'failed')
        self.assertIn('connection error', job.error_message)
