"""Adapter for the LA County Assessor PAIS Sales Parcels ArcGIS REST layer.

This is publicly accessible data with no robots.txt restriction (the host
returns 404 for /robots.txt, which RFC 9309 treats as no-policy = open).
The layer contains a row per parcel with a recorded sale, including
parcel ID, situs address, building size, year built, last sale date,
last sale price, and a four-digit USECODE.

For off-market leads we filter to commercial/industrial USETYPE='C/I'
with retail use codes (1xxx range — stores, single-tenant retail,
shopping centers, restaurants), constrain SIZE <= the configured cap,
and score "stale ownership" (sale > N years ago) as a stronger
off-market signal because long-held parcels are statistically less
likely to be actively marketed.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import List

from .base import BaseAdapter
from ..models import PropertyRecord

log = logging.getLogger(__name__)


SERVICE_URL = (
    "https://assessor.gis.lacounty.gov/assessor/rest/services/"
    "PAIS/pais_sales_parcels/MapServer/0/query"
)
PAGE_SIZE = 1000  # service maxRecordCount


# Maps USECODE prefixes to a human-readable retail subtype. Use codes are
# documented by the LA County Assessor; only the 1xxx range is retail.
USECODE_SUBTYPE = {
    "1100": "Store, retail",
    "1101": "Store with apartments",
    "1200": "Store with residential",
    "1210": "Store with residential, mixed",
    "1300": "Department store",
    "1400": "Supermarket",
    "1500": "Single-tenant retail",
    "1600": "Auto retail / service",
    "1700": "Shopping center / strip retail",
    "1800": "Restaurant",
    "1900": "Retail, other",
}


class LAPAISAdapter(BaseAdapter):
    name = "la_pais"

    def fetch(self) -> List[PropertyRecord]:
        if "CA" not in self.config.states:
            log.info("[%s] CA not in target states — skipping", self.name)
            return []

        max_sqft = int(self.config.max_total_sqft)
        where = (
            "USETYPE='C/I' AND USECODE LIKE '1%' "
            f"AND SIZE > 0 AND SIZE <= {max_sqft}"
        )
        out_fields = ",".join([
            "AIN", "FORMATTED_AIN", "SAADDR", "SALEDATE", "SALEPRICE",
            "SIZE", "YEARBUILT", "USECODE", "USETYPE",
        ])

        records: List[PropertyRecord] = []
        offset = 0
        while True:
            params = {
                "where": where,
                "outFields": out_fields,
                "f": "json",
                "returnGeometry": "false",
                "orderByFields": "SALEDATE ASC",  # stale ownership first
                "resultOffset": str(offset),
                "resultRecordCount": str(PAGE_SIZE),
            }
            resp = self.http.get(SERVICE_URL, params=params)
            if not resp:
                break
            try:
                payload = resp.json()
            except ValueError:
                log.warning("[%s] non-JSON page at offset %d", self.name, offset)
                break

            features = payload.get("features", [])
            if not features:
                break

            for feat in features:
                rec = self._to_record(feat.get("attributes") or {})
                if rec is not None:
                    records.append(rec)

            if not payload.get("exceededTransferLimit"):
                break
            offset += PAGE_SIZE
            # Stop once we comfortably exceed the target so we don't run forever.
            if len(records) >= self.config.target_count * 5:
                break

        self._log_count(records)
        return records

    def _to_record(self, a: dict) -> PropertyRecord | None:
        size = a.get("SIZE")
        if not size or size <= 0 or size > self.config.max_total_sqft:
            return None
        usecode = (a.get("USECODE") or "").strip()
        subtype = USECODE_SUBTYPE.get(usecode, f"Use code {usecode}")

        # SALEDATE is epoch-ms.
        last_sale = a.get("SALEDATE")
        if last_sale:
            sale_dt = datetime.fromtimestamp(int(last_sale) / 1000, tz=timezone.utc)
            years_held = (datetime.now(timezone.utc) - sale_dt).days / 365.25
        else:
            sale_dt = None
            years_held = None

        # Off-market signal logic: long-held owner-occupant retail parcel.
        if years_held is not None and years_held >= 7:
            signal = "stale_ownership_long_hold"
        elif years_held is not None and years_held >= 3:
            signal = "owner_held_retail"
        else:
            signal = "assessor_owner_lead"

        notes_bits = [
            f"USECODE={usecode} ({subtype})",
            f"SIZE={size} sqft",
            f"YEAR_BUILT={a.get('YEARBUILT', '?')}",
        ]
        if sale_dt:
            notes_bits.append(f"LAST_SALE={sale_dt.date().isoformat()}")
        if a.get("SALEPRICE"):
            notes_bits.append(f"LAST_SALE_PRICE=${int(a['SALEPRICE']):,}")
        if years_held is not None:
            notes_bits.append(f"YEARS_HELD={years_held:.1f}")

        return PropertyRecord(
            apn=a.get("FORMATTED_AIN") or a.get("AIN"),
            address=(a.get("SAADDR") or "").strip() or None,
            state="CA",
            property_type="Retail",
            retail_subtype=subtype,
            total_sqft=float(size),
            status="Owner-Held Retail Parcel (Not Listed)",
            off_market_signal=signal,
            source_url=(
                "https://assessor.gis.lacounty.gov/assessor/rest/services/"
                "PAIS/pais_sales_parcels/MapServer/0"
            ),
            source_name=self.name,
            notes="; ".join(notes_bits),
        )
