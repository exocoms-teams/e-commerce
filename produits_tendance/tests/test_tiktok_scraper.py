import json
from unittest.mock import MagicMock, patch

from odoo.tests.common import HttpCase, TransactionCase

from ..collecte_scrapers.tiktok_creative_center_scraper import (
    build_ad_payload,
    fetch_trending_ads_page,
    run_tiktok_ingestion,
)


class TestBuildAdPayload(TransactionCase):
    """WIN-69 : vérifie que build_ad_payload() respecte le contrat JSON
    "ad" attendu par /api/trend/ingest, quel que soit le nom de champ
    utilisé par Creative Center pour les likes/shares (cf. note en tête de
    tiktok_creative_center_scraper.py sur l'incertitude des noms de champs)."""

    def test_maps_standard_fields(self):
        item = {
            "id": "7123456789",
            "ad_title": "Montre connectée sport",
            "like": 1500,
            "share": 42,
        }
        payload = build_ad_payload(item, country_code='MA')

        self.assertEqual(payload['type'], 'ad')
        data = payload['data']
        self.assertEqual(data['ad_ref'], 'tiktok-7123456789')
        self.assertEqual(data['product_ref'], 'tiktok-product-7123456789')
        self.assertEqual(data['product_name'], 'Montre connectée sport')
        self.assertEqual(data['country'], 'MA')
        self.assertEqual(data['social_network'], 'tiktok')
        self.assertEqual(data['likes_count'], 1500)
        self.assertEqual(data['shares_count'], 42)

    def test_falls_back_to_alternate_field_names(self):
        """Si Creative Center renvoie like_count/share_count au lieu de
        like/share (variante de schéma), le mapping doit rester correct."""
        item = {
            "item_id": "999",
            "title": "Sac à dos randonnée",
            "like_count": 300,
            "share_count": 5,
        }
        payload = build_ad_payload(item, country_code='FR')

        self.assertEqual(payload['data']['ad_ref'], 'tiktok-999')
        self.assertEqual(payload['data']['product_name'], 'Sac à dos randonnée')
        self.assertEqual(payload['data']['likes_count'], 300)
        self.assertEqual(payload['data']['shares_count'], 5)

    def test_returns_none_without_identifier(self):
        """Une entrée sans id/item_id/ad_id exploitable ne doit jamais
        produire un payload avec un ad_ref bidon."""
        self.assertIsNone(build_ad_payload({"ad_title": "Sans id"}, country_code='MA'))

    def test_missing_engagement_fields_default_to_zero(self):
        payload = build_ad_payload({"id": "42"}, country_code='MA')
        self.assertEqual(payload['data']['likes_count'], 0)
        self.assertEqual(payload['data']['shares_count'], 0)


class TestFetchTrendingAdsPage(TransactionCase):
    """WIN-69 : fetch_trending_ads_page() ne doit jamais lever d'exception
    ni renvoyer None, quel que soit l'aléa réseau/HTTP (même contrat de
    robustesse que ebay_ingestor.fetch_winning_products)."""

    def test_returns_materials_on_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"materials": [{"id": "1"}, {"id": "2"}]}
        }
        with patch(
            'odoo.addons.produits_tendance.collecte_scrapers.tiktok_creative_center_scraper.requests.get',
            return_value=mock_response,
        ):
            items = fetch_trending_ads_page(page=1)
        self.assertEqual(len(items), 2)

    def test_returns_empty_list_on_http_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 403
        with patch(
            'odoo.addons.produits_tendance.collecte_scrapers.tiktok_creative_center_scraper.requests.get',
            return_value=mock_response,
        ):
            self.assertEqual(fetch_trending_ads_page(page=1), [])

    def test_returns_empty_list_on_network_error(self):
        import requests as requests_module
        with patch(
            'odoo.addons.produits_tendance.collecte_scrapers.tiktok_creative_center_scraper.requests.get',
            side_effect=requests_module.exceptions.ConnectionError("boom"),
        ):
            self.assertEqual(fetch_trending_ads_page(page=1), [])


class TestTikTokIngestionEndToEnd(HttpCase):
    """WIN-69 : vérifie que run_tiktok_ingestion() (le point d'entrée
    synchrone appelé par le contrôleur) insère bien des trend.ad réels via
    /api/trend/ingest, en ne mockant QUE l'appel réseau sortant vers
    TikTok - le trajet vers Odoo passe par le vrai endpoint HTTP, comme
    test_ad_ingestion.py le fait pour l'ingestion eBay."""

    def setUp(self):
        super().setUp()
        self.api_key = 'test-tiktok-key'
        self.env['ir.config_parameter'].sudo().set_param('winners.api_key', self.api_key)

    def test_run_tiktok_ingestion_creates_trend_ads(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "materials": [
                    {"id": "111", "ad_title": "Casque audio", "like": 800, "share": 12},
                    {"id": "222", "ad_title": "Lampe LED", "like": 400, "share": 3},
                ]
            }
        }
        with patch(
            'odoo.addons.produits_tendance.collecte_scrapers.tiktok_creative_center_scraper.requests.get',
            return_value=mock_response,
        ):
            result = run_tiktok_ingestion(
                odoo_url=f"{self.base_url()}/api/trend/ingest",
                odoo_api_key=self.api_key,
                pages=1,
            )

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['scanned'], 2)
        self.assertEqual(result['inserted'], 2)

        ads = self.env['trend.ad'].search([('ad_ref', 'in', ['tiktok-111', 'tiktok-222'])])
        self.assertEqual(len(ads), 2)
        self.assertEqual(sorted(ads.mapped('likes_count')), [400, 800])
        self.assertTrue(all(ad.social_network == 'tiktok' for ad in ads))

        products = self.env['trend.product'].search([
            ('product_ref', 'in', ['tiktok-product-111', 'tiktok-product-222']),
        ])
        self.assertEqual(len(products), 2)
        self.assertIn('Casque audio', products.mapped('name'))
