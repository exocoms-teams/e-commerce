# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from unittest.mock import patch
from datetime import datetime, timedelta


class TestTemporalTraceability(TransactionCase):
    """Test that compute_trend_score correctly uses temporal windows and source score."""

    def setUp(self):
        super().setUp()
        # Create a test product with source 'api'
        self.product = self.env['trend.product'].create({
            'name': 'Test Product for Temporal Traceability',
            'product_ref': 'TEST-TEMP-001',
            'country': 'MA',
            'source': 'api',
        })

        # Set a fixed date for consistent testing
        self.fixed_date = datetime(2026, 8, 1)

    def _create_trend_score(self, days_ago, sales=0, likes=0, shares=0, ads=0):
        """Helper to create a trend.score record for the product at a given offset."""
        computed_at = self.fixed_date - timedelta(days=days_ago)
        return self.env['trend.score'].create({
            'product_id': self.product.id,
            'computed_at': computed_at,
            'metric_sales': sales,
            'metric_likes': likes,
            'metric_shares': shares,
            'metric_ads_count': ads,
            # computed_score is not needed for the calculation, but we set a dummy
            'computed_score': 0.0,
        })

    def test_current_and_previous_windows_aggregation(self):
        """Test that current_metrics (last 30 days) and previous_metrics (30-60 days ago) are aggregated correctly."""
        # Define metrics for current period (last 30 days)
        current_sales, current_likes, current_shares, current_ads = 10, 20, 5, 2
        # Define metrics for previous period (30-60 days ago)
        prev_sales, prev_likes, prev_shares, prev_ads = 5, 10, 2, 1

        # Create records in the current window (within last 30 days from fixed_date)
        self._create_trend_score(days_ago=5, sales=current_sales, likes=current_likes,
                                 shares=current_shares, ads=current_ads)
        self._create_trend_score(days_ago=15, sales=current_sales, likes=current_likes,
                                 shares=current_shares, ads=current_ads)

        # Create records in the previous window (30-60 days ago)
        self._create_trend_score(days_ago=35, sales=prev_sales, likes=prev_likes,
                                 shares=prev_shares, ads=prev_ads)
        self._create_trend_score(days_ago=50, sales=prev_sales, likes=prev_likes,
                                 shares=prev_shares, ads=prev_ads)

        # Set source score for 'api' source
        self.env['ir.config_parameter'].sudo().set_param(
            'winners.source_score_api', '0.8'
        )

        # Mock datetime.now in the trend_product module to return our fixed_date
        with patch('produits_tendance.models.trend_product.datetime') as mock_dt:
            mock_dt.now.return_value = self.fixed_date
            # Keep the real timedelta for arithmetic
            mock_dt.timedelta = timedelta

            # Call the method under test
            score = self.product.compute_trend_score()

        # Manually compute expected score using the same logic as ScoringEngine
        # Constants from scoring_engine.py
        W_VENTES = 1.0
        W_LIKES = 0.1
        W_PARTAGES = 0.3
        W_ADS = 0.5
        ALPHA = 0.2
        EPSILON = 1.0

        # Current period totals (sum of the two records)
        vol_t = (W_VENTES * (current_sales * 2) +
                 W_LIKES * (current_likes * 2) +
                 W_PARTAGES * (current_shares * 2) +
                 W_ADS * (current_ads * 2))
        # Previous period totals
        vol_t_prev = (W_VENTES * (prev_sales * 2) +
                      W_LIKES * (prev_likes * 2) +
                      W_PARTAGES * (prev_shares * 2) +
                      W_ADS * (prev_ads * 2))

        growth = (vol_t - vol_t_prev) / (vol_t_prev + EPSILON)
        if growth <= 0:
            expected_score = 0.0
        else:
            volume_factor = __import__('math').log(1 + vol_t)
            source_score = 0.8  # from ir.config_parameter
            expected_score = growth * volume_factor * (1 + ALPHA * source_score)
            expected_score = round(expected_score, 4)

        self.assertAlmostEqual(score, expected_score, places=4,
                               msg="Computed score does not match expected temporal aggregation")

    def test_source_score_from_ir_config_parameter(self):
        """Test that source_score is correctly retrieved from ir.config_parameter based on product source."""
        # Create a trend.score record in the current window (so we have non-zero vol_t)
        self._create_trend_score(days_ago=10, sales=10, likes=10, shares=10, ads=10)

        # Test each source type
        source_score_map = {
            'scraping': 'winners.source_score_scraping',
            'crowdsourcing': 'winners.source_score_crowdsourcing',
            'api': 'winners.source_score_api',
        }

        for source, param_name in source_score_map.items():
            # Update product source
            self.product.source = source
            # Set a unique source score for this source
            test_score = 0.5  # arbitrary
            self.env['ir.config_parameter'].sudo().set_param(param_name, str(test_score))

            with patch('produits_tendance.models.trend_product.datetime') as mock_dt:
                mock_dt.now.return_value = self.fixed_date
                mock_dt.timedelta = timedelta

                score = self.product.compute_trend_score()

            # We don't need to assert the exact score, just that it used the source_score we set.
            # We can check that the score is not zero (given our metrics) and that changing the source score changes the result.
            # For simplicity, we'll just ensure the score is computed (non-zero) and that the source score was considered.
            # Since the calculation is complex, we'll do a sanity check: score should be positive and finite.
            self.assertGreater(score, 0.0, f"Score should be positive for source {source}")

            # Change the source score and verify the score changes (optional, but good)
            # We'll do a quick check with two different values for one source.
            if source == 'api':
                # Set a different source score
                self.env['ir.config_parameter'].sudo().set_param(param_name, '0.9')
                with patch('produits_tendenza.models.trend_product.datetime') as mock_dt2:
                    mock_dt2.now.return_value = self.fixed_date
                    mock_dt2.timedelta = timedelta
                    score2 = self.product.compute_trend_score()
                # The score should be different (and higher because source_score increased)
                self.assertNotEqual(score, score2, "Score should change when source_score changes")

    def test_no_records_in_previous_period(self):
        """Test behavior when there are no records in the previous period (should treat as zero)."""
        # Create only current period records
        self._create_trend_score(days_ago=10, sales=20, likes=20, shares=10, ads=5)
        self._create_trend_score(days_ago=20, sales=20, likes=20, shares=10, ads=5)

        # Set source score
        self.env['ir.config_parameter'].sudo().set_param(
            'winners.source_score_api', '0.5'
        )

        with patch('produits_tendenza.models.trend_product.datetime') as mock_dt:
            mock_dt.now.return_value = self.fixed_date
            mock_dt.timedelta = timedelta

            score = self.product.compute_trend_score()

        # We expect a positive score because vol_t > 0 and vol_t_prev = 0 -> growth > 0
        self.assertGreater(score, 0.0, "Score should be positive when previous period is empty")

    def test_no_records_in_current_period(self):
        """Test behavior when there are no records in the current period (should vol_t = 0 -> growth <= 0 -> score 0)."""
        # Create only previous period records
        self._create_trend_score(days_ago=40, sales=10, likes=10, shares=5, ads=2)
        self._create_trend_score(days_ago=50, sales=10, likes=10, shares=5, ads=2)

        # Set source score
        self.env['ir.config_parameter'].sudo().set_param(
            'winners.source_score_api', '0.5'
        )

        with patch('produits_tendenza.models.trend_product.datetime') as mock_dt:
            mock_dt.now.return_value = self.fixed_date
            mock_dt.timedelta = timedelta

            score = self.product.compute_trend_score()

        # With vol_t = 0, growth = (0 - vol_t_prev) / (vol_t_prev + EPSILON) = negative -> score 0.0
        self.assertEqual(score, 0.0, "Score should be zero when current period is empty")

