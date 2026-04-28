"""CSV / JSON / markdown writers."""
from __future__ import annotations

import csv
import json
import logging
import os
from collections import Counter
from datetime import datetime, timezone
from typing import List

from .models import PropertyRecord, RejectedCandidate

log = logging.getLogger(__name__)


CSV_FIELDS = [
    "property_name", "address", "city", "state", "zip_code", "apn",
    "property_type", "retail_subtype",
    "total_sqft", "available_sqft", "lot_size_sqft",
    "status", "off_market_signal",
    "source_url", "source_name",
    "contact_name", "contact_phone", "contact_email",
    "asking_price", "lease_rate",
    "notes", "confidence_score", "completeness_score", "captured_at",
]


def _ensure_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def write_csv(path: str, records: List[PropertyRecord]) -> None:
    _ensure_dir(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.to_dict().get(k) for k in CSV_FIELDS})
    log.info("wrote %d records to %s", len(records), path)


def write_json(path: str, records: List[PropertyRecord]) -> None:
    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in records], f, indent=2, default=str)
    log.info("wrote %d records to %s", len(records), path)


def write_rejected(path: str, rejected: List[RejectedCandidate]) -> None:
    _ensure_dir(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["reason"] + CSV_FIELDS)
        writer.writeheader()
        for rc in rejected:
            row = {k: rc.record.to_dict().get(k) for k in CSV_FIELDS}
            row["reason"] = rc.reason
            writer.writerow(row)
    log.info("wrote %d rejected candidates to %s", len(rejected), path)


def write_summary(
    path: str,
    *,
    total_candidates: int,
    valid_records: List[PropertyRecord],
    rejected: List[RejectedCandidate],
    notable_logic: List[str],
) -> None:
    _ensure_dir(path)
    by_source = Counter(r.source_name or "unknown" for r in valid_records)
    by_signal = Counter(r.off_market_signal or "unknown" for r in valid_records)
    rej_reasons = Counter(rc.reason for rc in rejected)

    lines = [
        "# Off-Market Retail Property Scrape — Summary",
        "",
        f"- Run timestamp (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Total raw candidates collected: **{total_candidates}**",
        f"- Total valid properties after filter+dedupe: **{len(valid_records)}**",
        f"- Total rejected: **{len(rejected)}**",
        "",
        "## Source breakdown",
    ]
    for src, n in by_source.most_common():
        lines.append(f"- `{src}`: {n}")
    lines.append("")
    lines.append("## Off-market signal breakdown")
    for sig, n in by_signal.most_common():
        lines.append(f"- `{sig}`: {n}")
    lines.append("")
    lines.append("## Rejection reasons")
    for reason, n in rej_reasons.most_common():
        lines.append(f"- `{reason}`: {n}")
    lines.append("")
    lines.append("## Notable filtering / scoring logic")
    for note in notable_logic:
        lines.append(f"- {note}")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log.info("wrote summary to %s", path)
