import json

from odoo.tests.common import HttpCase
from odoo.tools import mute_logger
from ..models.trend_ad import latest_ads_by_ref

class TestAdIngestionHistorization(HttpCase):
    """WIN-XX ('Passer trend.ad en mode historique') : le handler 'ad' de
    /api/trend/ingest ne doit plus écraser likes_count/shares_count sur un
    enregistrement existant, mais créer une nouvelle ligne trend.ad
    horodatée à chaque collecte.

    Reprend le test d'acceptation décrit dans le ticket : envoyer 2 fois le
    même product_ref/ad_ref avec des likes_count différents, à un jour
    d'intervalle, et vérifier que les 2 valeurs coexistent en base (2
    lignes), pas une seule écrasée.
    """

    def setUp(self):
        super().setUp()
        self.api_key = 'test-ingest-key'
        self.env['ir.config_parameter'].sudo().set_param('winners.api_key', self.api_key)
        self.product = self.env['trend.product'].create({
            'name': 'Produit test ingestion ad',
            'product_ref': 'TEST-INGEST-AD-0001',
            'country': 'MA',
            'source': 'api',
        })

    def _ingest_ad(self, likes_count, shares_count, collected_at=None):
        data = {
            'ad_ref': 'TEST-INGEST-AD-REF-0001',
            'product_ref': self.product.product_ref,
            'country': 'MA',
            'social_network': 'facebook',
            'likes_count': likes_count,
            'shares_count': shares_count,
        }
        if collected_at:
            data['collected_at'] = collected_at

        response = self.url_open(
            '/api/trend/ingest',
            data=json.dumps({'api_key': self.api_key, 'type': 'ad', 'data': data}),
            headers={'Content-Type': 'application/json'},
        )
        return json.loads(response.text)

    @mute_logger('odoo.sql_db', 'odoo.http')
    def test_sending_same_ad_ref_twice_creates_two_historized_rows(self):
        result_1 = self._ingest_ad(likes_count=100, shares_count=10, collected_at='2026-07-01 09:00:00')
        result_2 = self._ingest_ad(likes_count=250, shares_count=40, collected_at='2026-07-02 09:00:00')

        self.assertEqual(result_1.get('status'), 'success')
        self.assertEqual(result_2.get('status'), 'success')
        self.assertNotEqual(result_1['id'], result_2['id'])

        ads = self.env['trend.ad'].search([('ad_ref', '=', 'TEST-INGEST-AD-REF-0001')])
        self.assertEqual(len(ads), 2)
        self.assertEqual(sorted(ads.mapped('likes_count')), [100, 250])

    def test_current_metrics_count_each_ad_once_despite_history(self):
        """Sans latest_ads_by_ref, sum(ad_ids.mapped('likes_count')) sur un
        produit avec 2 collectes historisées de la MÊME publicité donnerait
        100+250=350 au lieu de 250 (dernier snapshot uniquement)."""
        self._ingest_ad(likes_count=100, shares_count=10, collected_at='2026-07-01 09:00:00')
        self._ingest_ad(likes_count=250, shares_count=40, collected_at='2026-07-02 09:00:00')

        latest_ads = latest_ads_by_ref(self.product.ad_ids)
        self.assertEqual(sum(latest_ads.mapped('likes_count')), 250)
        self.assertEqual(sum(latest_ads.mapped('shares_count')), 40)
        self.assertEqual(len(latest_ads), 1)