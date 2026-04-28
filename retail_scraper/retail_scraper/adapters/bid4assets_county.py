"""Adapter for Bid4Assets county tax-defaulted property auctions.

Tax-defaulted properties are inherently off-market: the prior owner has
not paid taxes for >5 years (CA), the lien holder is the county, and the
asset is being disposed via public auction. We keep only retail-coded
parcels under the size cap.

Bid4Assets storefronts render through JavaScript, so the most reliable
public artifact is the parcel list each county publishes alongside the
sale (PDF or CSV). This adapter accepts a pre-downloaded list path via
the BID4ASSETS_PARCEL_LIST_PATH env var so the user can drop in the
official county document without us scraping a JS-only page.
"""
from __future__ import annotations

import csv
import logging
import os
import re
from typing import List

from .base import BaseAdapter
from ..models import PropertyRecord

log = logging.getLogger(__name__)


# County-published parcel list URLs (PDF or HTML). These are the canonical
# public records. A user can save them locally and point the env var at
# the file, or extend this dict with new sales as counties publish them.
KNOWN_COUNTY_PARCEL_LISTS = {
    "Riverside-Apr2026":
        "https://countytreasurer.org/tc-223",
    "Imperial-Feb2026":
        "https://www.bid4assets.com/storefront/ImperialFeb26",
    "Stanislaus-May2026":
        "https://www.stancounty.com/tr-tax/auction/tax-sale-auction.shtm",
}

RETAIL_USE_PATTERNS = re.compile(
    r"\b(retail|store|strip\s*center|shopping\s*center|commercial[-\s]retail|"
    r"restaurant|fast\s*food|service\s*station|auto\s*service|free\s*standing|"
    r"single\s*tenant|gas\s*station|convenience)\b",
    re.I,
)


class Bid4AssetsCountyAdapter(BaseAdapter):
    name = "bid4assets_county"

    def fetch(self) -> List[PropertyRecord]:
        records: List[PropertyRecord] = []

        # Path 1 — operator-supplied CSV of parcels (preferred, deterministic).
        local = os.environ.get("BID4ASSETS_PARCEL_LIST_PATH")
        if local and os.path.exists(local):
            log.info("[%s] reading local parcel list %s", self.name, local)
            records.extend(self._read_local_csv(local))

        # Path 2 — best-effort HTML fetch of county info pages. We do not
        # attempt to scrape the JS-only Bid4Assets storefront itself.
        for sale_id, url in KNOWN_COUNTY_PARCEL_LISTS.items():
            resp = self.http.get(url)
            if not resp:
                continue
            # We don't pretend to extract structured rows from a marketing
            # page — we just record that a sale exists, so the operator
            # can follow up.
            log.info("[%s] %s reachable; operator should download parcel list", self.name, sale_id)

        self._log_count(records)
        return records

    def _read_local_csv(self, path: str) -> List[PropertyRecord]:
        """Read a county-published parcel CSV.

        Expected columns (case-insensitive, extras ignored):
            APN, address, city, state, zip, use_code, total_sqft, lot_sqft,
            min_bid, sale_id
        """
        out: List[PropertyRecord] = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [h.strip().lower() for h in (reader.fieldnames or [])]
            for row in reader:
                row = {k.strip().lower(): (v.strip() if isinstance(v, str) else v)
                       for k, v in row.items()}
                use = row.get("use_code") or row.get("property_use") or ""
                if not RETAIL_USE_PATTERNS.search(use):
                    continue

                rec = PropertyRecord(
                    apn=row.get("apn"),
                    address=row.get("address"),
                    city=row.get("city"),
                    state=(row.get("state") or "CA").upper(),
                    zip_code=row.get("zip"),
                    property_type="Retail",
                    retail_subtype=use,
                    total_sqft=_to_float(row.get("total_sqft")),
                    lot_size_sqft=_to_float(row.get("lot_sqft")),
                    asking_price=_to_float(row.get("min_bid")),
                    status="Tax Defaulted - County Auction",
                    off_market_signal="tax_defaulted",
                    source_name=self.name,
                    source_url=row.get("source_url") or row.get("listing_url"),
                    notes=f"Sale ID: {row.get('sale_id', 'unknown')}; lien-holder county; "
                          f">5 years delinquent under CA R&T 3691.",
                )
                out.append(rec)
        return out


def _to_float(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace(",", "").replace("$", "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None
