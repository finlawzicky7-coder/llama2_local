"""Top-level orchestrator: drives adapters, pipeline, and writers."""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from typing import List

from .adapters import (
    Bid4AssetsCountyAdapter,
    FDICOREAdapter,
    GSARealEstateSalesAdapter,
    LAPAISAdapter,
    SBAOREOAdapter,
)
from .config import ScraperConfig
from .http import HttpClient
from .models import PropertyRecord, RejectedCandidate
from .output import write_csv, write_json, write_rejected, write_summary
from .pipeline import dedupe_records, filter_records, rank_records, score_records


def _setup_logging(config: ScraperConfig) -> None:
    os.makedirs(config.log_dir, exist_ok=True)
    log_path = os.path.join(
        config.log_dir, f"run-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.log",
    )
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path, encoding="utf-8"),
    ]
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def run(config: ScraperConfig | None = None) -> int:
    config = config or ScraperConfig()
    _setup_logging(config)
    log = logging.getLogger("runner")

    http = HttpClient(
        user_agent=config.user_agent,
        timeout=config.request_timeout_sec,
        retries=config.request_retries,
        backoff=config.request_backoff_sec,
        throttle=config.request_throttle_sec,
    )

    adapters = []
    if config.enable_gsa:
        adapters.append(GSARealEstateSalesAdapter(config, http))
    if config.enable_fdic_ore:
        adapters.append(FDICOREAdapter(config, http))
    if config.enable_bid4assets:
        adapters.append(Bid4AssetsCountyAdapter(config, http))
    if config.enable_sba_oreo:
        adapters.append(SBAOREOAdapter(config, http))
    if config.enable_la_pais:
        adapters.append(LAPAISAdapter(config, http))

    raw: List[PropertyRecord] = []
    for adapter in adapters:
        log.info("running adapter: %s", adapter.name)
        try:
            raw.extend(adapter.fetch())
        except Exception:
            log.exception("adapter %s failed", adapter.name)

    log.info("collected %d raw candidates from %d adapter(s)", len(raw), len(adapters))

    kept, rejected = filter_records(raw, config)
    deduped = dedupe_records(kept)
    score_records(deduped)
    ranked = rank_records(deduped)

    final = ranked[: config.target_count]
    if len(final) < config.target_count:
        log.warning(
            "only %d valid record(s) found; target was %d. "
            "See SUMMARY.md for source-by-source breakdown.",
            len(final), config.target_count,
        )

    write_csv(config.output_csv, final)
    write_json(config.output_json, final)
    write_rejected(config.output_rejected_csv, rejected)
    write_summary(
        config.output_summary_md,
        total_candidates=len(raw),
        valid_records=final,
        rejected=rejected,
        notable_logic=[
            "Strict retail filter using a regex over property_type/subtype/notes.",
            f"Hard size cap at {int(config.max_total_sqft):,} sqft.",
            "Geography filter against configured target states.",
            "Dedupe key: APN > address+city+state > name+city > source URL.",
            "Confidence score weighted by off-market signal "
            "(tax-defaulted > FDIC OREO > GSA surplus > government auction > "
            "withdrawn/expired > assessor-only).",
            "Records sorted by confidence_score then completeness_score.",
            "Robots.txt is checked per-host before every request; disallowed URLs are skipped.",
            "All adapter failures are caught so partial runs still produce output.",
        ],
    )
    return 0
