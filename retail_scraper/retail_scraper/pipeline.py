"""Pipeline: filter -> dedupe -> score -> rank."""
from __future__ import annotations

import logging
import re
from typing import Iterable, List, Tuple

from .config import ScraperConfig
from .models import PropertyRecord, RejectedCandidate

log = logging.getLogger(__name__)


# Used to detect a retail-ish property type. Retail is the only allowed
# primary class; all other types are rejected.
RETAIL_PATTERN = re.compile(
    r"\bretail|store|strip\s*center|shopping|restaurant|fast\s*food|"
    r"service\s*station|gas\s*station|auto\s*service|free[-\s]?standing|"
    r"single\s*tenant|convenience\b",
    re.I,
)

# Confidence weights for off-market signals.
OFF_MARKET_WEIGHTS = {
    "tax_defaulted": 0.95,                # county is auctioning, owner gone
    "fdic_oreo": 0.90,                    # FDIC receiver, failed bank asset
    "federal_surplus": 0.85,              # GSA disposing, never on MLS
    "government_auction": 0.80,           # GovDeals/SBA collateral
    "withdrawn": 0.70,                    # explicitly withdrawn listing
    "expired": 0.65,                      # expired listing
    "stale_ownership_long_hold": 0.65,    # 7+ years held, owner-occupant
    "owner_held_retail": 0.55,            # 3+ years held
    "assessor_owner_lead": 0.50,          # owner-occupant from assessor data
    "owner_listed": 0.50,                 # for-sale-by-owner — sometimes
    None: 0.40,
}


def filter_records(
    records: Iterable[PropertyRecord],
    config: ScraperConfig,
) -> Tuple[List[PropertyRecord], List[RejectedCandidate]]:
    kept: List[PropertyRecord] = []
    rejected: List[RejectedCandidate] = []

    for r in records:
        # Geography filter (when state is known).
        if r.state and config.states and r.state.upper() not in config.states:
            rejected.append(RejectedCandidate(r, "state_outside_target"))
            continue

        # Retail filter — strict.
        descriptors = " ".join(filter(None, [r.property_type, r.retail_subtype, r.notes]))
        if not RETAIL_PATTERN.search(descriptors or ""):
            rejected.append(RejectedCandidate(r, "non_retail_or_unknown_type"))
            continue

        # Size filter.
        if r.total_sqft is not None and r.total_sqft > config.max_total_sqft:
            rejected.append(RejectedCandidate(r, f"over_{int(config.max_total_sqft)}_sqft"))
            continue

        # Drop completely empty records.
        if not any([r.address, r.apn, r.property_name]):
            rejected.append(RejectedCandidate(r, "no_identity_fields"))
            continue

        kept.append(r)

    log.info("filter: kept %d, rejected %d", len(kept), len(rejected))
    return kept, rejected


def dedupe_records(records: List[PropertyRecord]) -> List[PropertyRecord]:
    seen: dict[str, PropertyRecord] = {}
    for r in records:
        key = r.dedupe_key()
        if key not in seen:
            seen[key] = r
            continue
        # If we have a duplicate, keep the more complete record.
        if _completeness(r) > _completeness(seen[key]):
            seen[key] = r
    log.info("dedupe: %d unique from %d", len(seen), len(records))
    return list(seen.values())


def score_records(records: List[PropertyRecord]) -> None:
    """Mutates records to set confidence_score and completeness_score."""
    for r in records:
        r.confidence_score = OFF_MARKET_WEIGHTS.get(r.off_market_signal,
                                                    OFF_MARKET_WEIGHTS[None])
        r.completeness_score = _completeness(r)


def rank_records(records: List[PropertyRecord]) -> List[PropertyRecord]:
    return sorted(
        records,
        key=lambda r: (r.confidence_score, r.completeness_score),
        reverse=True,
    )


def _completeness(r: PropertyRecord) -> float:
    fields = [
        r.property_name, r.address, r.city, r.state, r.zip_code, r.apn,
        r.property_type, r.retail_subtype, r.total_sqft, r.lot_size_sqft,
        r.status, r.off_market_signal, r.source_url, r.source_name,
    ]
    filled = sum(1 for f in fields if f not in (None, "", 0))
    return filled / len(fields)
