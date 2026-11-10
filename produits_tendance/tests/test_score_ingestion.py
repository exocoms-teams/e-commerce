import json

from odoo.tests.common import HttpCase
from odoo.tools import mute_logger


class TestScoreIngestion(HttpCase):
    """Association des scores calculés (cf. contrat_requets.md, section 3.2) :
    le handler 'score' de /api/trend/ingest doit rechercher le produit par
    product_ref, ne JAMAIS le créer automatiquement si absent (contrainte
    explicite du ticket, contrairement au handler 'ad'), et créer un
    trend.score lié si le produit existe.
    """

    def setUp(self):
        super().setUp()
        self.api_key = 'test-ingest-key'
        self.env['ir.config_parameter'].sudo().set_param('winners.api_key', self.api_key)
        self.product = self.env['trend.product'].create({
            'name': 'Produit test ingestion score',
            'product_ref': 'TEST-INGEST-SCORE-0001',
            'country': 'MA',
            'source': 'api',
        })

    def _ingest_score(self, product_ref, computed_score=82.4, computed_at=None):
        data = {
            'product_ref': product_ref,
            'computed_score': computed_score,
        }
        if computed_at:
            data['computed_at'] = computed_at

        return self.url_open(
            '/api/trend/ingest',
            data=json.dumps({'api_key': self.api_key, 'type': 'score', 'data': data}),
            headers={'Content-Type': 'application/json'},
        )

    @mute_logger('odoo.sql_db', 'odoo.http')
    def test_score_for_unknown_product_ref_returns_product_not_found(self):
        """Cas d'acceptation du ticket : envoyer un score pour un
        product_ref inexistant doit retourner product_not_found, et ne
        JAMAIS créer le produit ni le score en base."""
        products_before = self.env['trend.product'].search_count([])
        scores_before = self.env['trend.score'].search_count([])

        response = self._ingest_score(product_ref='FAUX_PRODUIT_123')
        payload = json.loads(response.text)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(payload.get('status'), 'error')
        self.assertEqual(payload.get('code'), 'product_not_found')

        # Contrainte du ticket : ne jamais forcer la création d'un produit
        # depuis un appel de type 'score'.
        self.assertEqual(
            self.env['trend.product'].search_count([]), products_before,
            "Aucun trend.product ne doit être créé pour un score sur une référence inconnue",
        )
        self.assertEqual(
            self.env['trend.score'].search_count([]), scores_before,
            "Aucun trend.score ne doit être créé si le produit est introuvable",
        )

    @mute_logger('odoo.sql_db', 'odoo.http')
    def test_score_for_existing_product_creates_trend_score(self):
        """Cas nominal : le score doit être créé et lié au bon produit."""
        response = self._ingest_score(
            product_ref=self.product.product_ref,
            computed_score=82.4,
            computed_at='2026-07-07 09:15:00',
        )
        payload = json.loads(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload.get('status'), 'success')
        self.assertEqual(payload.get('type'), 'score')

        score = self.env['trend.score'].browse(payload['id'])
        self.assertEqual(score.product_id, self.product)
        self.assertEqual(score.computed_score, 82.4)