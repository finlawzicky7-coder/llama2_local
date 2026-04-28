"""Adapter for FDIC Owned Real Estate listings.

FDIC OREO are bank-owned properties that hit the FDIC after receivership —
inherently off-market, distressed assets.
"""
from __future__ import annotations

import logging
import re
from typing import List

from bs4 import BeautifulSoup

from .base import BaseAdapter
from ..models import PropertyRecord

log = logging.getLogger(__name__)


LISTING_URL = "https://fdic-ore.com/listing.php"


class FDICOREAdapter(BaseAdapter):
    name = "fdic_ore"

    def fetch(self) -> List[PropertyRecord]:
        records: List[PropertyRecord] = []
        # Search by state when possible.
        for state in self.config.states:
            resp = self.http.get(LISTING_URL, params={"state": state})
            if not resp:
                continue
            records.extend(self._parse(resp.text, state))
        self._log_count(records)
        return records

    def _parse(self, html: str, state: str) -> List[PropertyRecord]:
        soup = BeautifulSoup(html, "html.parser")
        out: List[PropertyRecord] = []
        # Listings render as a table; we scan rows defensively.
        for row in soup.select("table tr"):
            cells = [c.get_text(" ", strip=True) for c in row.find_all("td")]
            if len(cells) < 3:
                continue
            text = " | ".join(cells)
            if not re.search(r"retail|commercial|store", text, re.I):
                continue

            link = row.find("a", href=True)
            url = link["href"] if link else None

            address, city, zip_code = self._split_address(cells)
            sqft = self._extract_sqft(text)

            out.append(PropertyRecord(
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                property_type="Retail" if re.search(r"retail|store", text, re.I) else "Commercial",
                total_sqft=sqft,
                status="FDIC OREO (Failed Bank Asset)",
                off_market_signal="fdic_oreo",
                source_url=url,
                source_name=self.name,
                notes="Owned by FDIC as receiver of a failed institution.",
            ))
        return out

    @staticmethod
    def _split_address(cells: List[str]) -> tuple[str | None, str | None, str | None]:
        # Best-effort parse of "123 Main St, Anytown, CA 90001".
        for c in cells:
            m = re.match(r"(.+?),\s*(.+?),\s*[A-Z]{2}\s*(\d{5})(?:-\d{4})?$", c)
            if m:
                return m.group(1).strip(), m.group(2).strip(), m.group(3)
        return None, None, None

    @staticmethod
    def _extract_sqft(text: str) -> float | None:
        m = re.search(r"([\d,]+)\s*(?:sq\s*ft|sf|square feet)", text, re.I)
        if not m:
            return None
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None
