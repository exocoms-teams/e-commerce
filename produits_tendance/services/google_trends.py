"""Collect informational Google Trends interest for a scoring date."""

import logging
import math
from datetime import timedelta

from odoo import fields

_logger = logging.getLogger(__name__)


def fetch_search_volume(product_name, country, computed_at):
    """Return the scoring day's Google Trends interest index (0–100).

    The historical field name is search_volume, but this value is
    relative search interest, not an absolute search count.

    Query one product name in its target country over seven days.
    Use only a reading dated on the requested scoring day.
    Today's reading may be partial.

    Missing data or collection failures return 0 and are logged.
    This value must never enter the trend score calculation.
    """
    keyword = (product_name or "").strip()
    geo = (country or "").strip().upper()
    scoring_date = fields.Datetime.to_datetime(computed_at).date()

    if not keyword:
        _logger.warning("Google Trends skipped: missing product name.")
        return 0

    if len(geo) != 2 or not geo.isalpha():
        _logger.warning(
            "Google Trends skipped for %s: invalid country %r.",
            keyword,
            geo,
        )
        return 0

    start_date = scoring_date - timedelta(days=6)
    timeframe = f"{start_date.isoformat()} {scoring_date.isoformat()}"

    try:
        from pytrends.request import TrendReq

        client = TrendReq(
            hl="en-US",
            tz=0,
            timeout=(5, 15),
            retries=0,
        )
        client.build_payload(
            [keyword],
            timeframe=timeframe,
            geo=geo,
        )
        readings = client.interest_over_time()

        if readings.empty or keyword not in readings.columns:
            _logger.warning(
                "No Google Trends data for %s on %s.",
                keyword,
                scoring_date,
            )
            return 0

        daily_readings = readings.loc[
            readings.index.date == scoring_date,
            keyword,
        ]

        if daily_readings.empty:
            _logger.warning(
                "No Google Trends reading for %s on %s.",
                keyword,
                scoring_date,
            )
            return 0

        value = float(daily_readings.iloc[-1])

        if not math.isfinite(value) or not 0 <= value <= 100:
            raise ValueError(f"Invalid Google Trends index: {value}")

        return int(round(value))

    except Exception:
        # An external collection failure must not stop daily scoring.
        _logger.exception(
            "Google Trends collection failed for %s (%s) on %s.",
            keyword,
            geo,
            scoring_date,
        )
        return 0