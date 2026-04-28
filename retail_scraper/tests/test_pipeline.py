"""Smoke tests for the filter / dedupe / score pipeline."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retail_scraper.config import ScraperConfig
from retail_scraper.models import PropertyRecord
from retail_scraper.pipeline import (
    dedupe_records,
    filter_records,
    rank_records,
    score_records,
)


def _rec(**kw) -> PropertyRecord:
    base = dict(
        property_type="Retail",
        state="CA",
        address="100 Main St",
        city="Anytown",
        zip_code="90001",
        total_sqft=5000.0,
        off_market_signal="tax_defaulted",
        source_name="test",
    )
    base.update(kw)
    return PropertyRecord(**base)


def test_filter_drops_oversize():
    cfg = ScraperConfig()
    keep, rej = filter_records([_rec(total_sqft=25_000)], cfg)
    assert keep == []
    assert rej and "over_" in rej[0].reason


def test_filter_drops_non_retail():
    cfg = ScraperConfig()
    keep, rej = filter_records([_rec(property_type="Office", retail_subtype=None, notes=None)], cfg)
    assert keep == []
    assert rej[0].reason == "non_retail_or_unknown_type"


def test_filter_drops_off_geography():
    cfg = ScraperConfig(states=["CA"])
    keep, rej = filter_records([_rec(state="NY")], cfg)
    assert keep == []
    assert rej[0].reason == "state_outside_target"


def test_filter_keeps_clean_record():
    cfg = ScraperConfig()
    keep, rej = filter_records([_rec()], cfg)
    assert len(keep) == 1
    assert rej == []


def test_dedupe_collapses_same_address():
    a = _rec(address="200 Oak St")
    b = _rec(address="200 Oak St", apn=None, total_sqft=None)
    out = dedupe_records([a, b])
    assert len(out) == 1
    # The more-complete record (with sqft) should win.
    assert out[0].total_sqft == 5000.0


def test_score_assigns_confidence():
    r = _rec(off_market_signal="tax_defaulted")
    score_records([r])
    assert r.confidence_score >= 0.9
    assert 0 < r.completeness_score <= 1


def test_rank_orders_by_confidence_then_completeness():
    high = _rec(off_market_signal="tax_defaulted")
    low = _rec(off_market_signal="owner_listed")
    score_records([high, low])
    out = rank_records([low, high])
    assert out[0] is high
    assert out[1] is low


if __name__ == "__main__":
    test_filter_drops_oversize()
    test_filter_drops_non_retail()
    test_filter_drops_off_geography()
    test_filter_keeps_clean_record()
    test_dedupe_collapses_same_address()
    test_score_assigns_confidence()
    test_rank_orders_by_confidence_then_completeness()
    print("all tests passed")
