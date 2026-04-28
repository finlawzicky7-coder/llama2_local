"""Runtime configuration for the scraper."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ScraperConfig:
    # Geography priority (used as default when a source supports multi-state).
    states: List[str] = field(default_factory=lambda: ["CA", "TX", "FL", "AZ", "NV", "GA"])

    # Search terms — combined by adapters that drive a search box.
    search_terms: List[str] = field(default_factory=lambda: [
        "retail",
        "retail building",
        "strip center",
        "free standing retail",
        "owner user retail",
        "available retail space",
        "off market retail",
        "withdrawn retail listing",
        "expired retail listing",
    ])

    # Hard filter limits.
    max_total_sqft: float = 20_000.0
    target_count: int = 50

    # HTTP behavior.
    request_timeout_sec: float = 20.0
    request_retries: int = 3
    request_backoff_sec: float = 2.0
    request_throttle_sec: float = 1.0
    user_agent: str = (
        "off-market-retail-scraper/0.1 (+research; respects robots.txt; "
        "contact: replace-with-your-email@example.com)"
    )

    # Output paths (relative to project root).
    output_csv: str = "outputs/retail_offmarket.csv"
    output_json: str = "outputs/retail_offmarket.json"
    output_rejected_csv: str = "outputs/retail_offmarket_rejected.csv"
    output_summary_md: str = "outputs/SUMMARY.md"

    # Logging.
    log_dir: str = "logs"
    log_level: str = "INFO"

    # Adapter toggles. Set to False to skip an adapter.
    enable_gsa: bool = True
    enable_fdic_ore: bool = True
    enable_bid4assets: bool = True
    enable_sba_oreo: bool = True
    enable_la_pais: bool = True
    enable_business_for_sale: bool = False  # off by default — most sources forbid scraping
