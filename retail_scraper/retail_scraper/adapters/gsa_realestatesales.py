"""Adapter for GSA realestatesales.gov — federal surplus real estate.

Properties listed here are by definition off-market in the conventional CRE sense:
they are federal surplus and routed through GSA disposal.
"""
from __future__ import annotations

import logging
import re
from typing import List

from bs4 import BeautifulSoup

from .base import BaseAdapter
from ..models import PropertyRecord

log = logging.getLogger(__name__)


LISTING_INDEX_URL = "https://realestatesales.gov/our-listing/"


class GSARealEstateSalesAdapter(BaseAdapter):
    name = "gsa_realestatesales"

    def fetch(self) -> List[PropertyRecord]:
        records: List[PropertyRecord] = []
        resp = self.http.get(LISTING_INDEX_URL)
        if not resp:
            log.info("[%s] no response from index", self.name)
            self._log_count(records)
            return records

        soup = BeautifulSoup(resp.text, "html.parser")
        # Listing tiles use <article class="listing-card"> in current site;
        # we keep the selector defensive in case markup shifts.
        for card in soup.select("article, div.listing-card, li.listing-item"):
            link = card.find("a", href=True)
            if not link:
                continue
            url = link["href"]
            title = (link.get_text() or "").strip()

            # Pull state from card text if present.
            text = card.get_text(" ", strip=True)
            state = self._extract_state(text)
            if self.config.states and state and state not in self.config.states:
                continue

            type_match = re.search(r"\b(Retail|Commercial|Industrial|Office|Land)\b", text, re.I)
            ptype = type_match.group(1).title() if type_match else None

            sqft = self._extract_sqft(text)

            records.append(PropertyRecord(
                property_name=title or None,
                state=state,
                property_type=ptype,
                total_sqft=sqft,
                status="GSA Surplus / Federal Disposal",
                off_market_signal="federal_surplus",
                source_url=url,
                source_name=self.name,
                notes="Federal surplus real estate listed by GSA — sold via auction or "
                      "negotiated disposal; not a conventional CRE listing.",
            ))

        self._log_count(records)
        return records

    @staticmethod
    def _extract_state(text: str) -> str | None:
        m = re.search(r",\s*([A-Z]{2})(?:\s|,|$)", text)
        return m.group(1) if m else None

    @staticmethod
    def _extract_sqft(text: str) -> float | None:
        m = re.search(r"([\d,]+)\s*(?:sq\s*ft|sf|square feet)", text, re.I)
        if not m:
            return None
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None
