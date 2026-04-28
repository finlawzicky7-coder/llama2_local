"""Adapter for SBA-acquired collateral / OREO.

The SBA periodically auctions collateral acquired in connection with
defaulted SBA loans. These are off-market by definition.

The SBA does not currently expose a clean JSON feed for the public
auction inventory; instead they post HTML auction announcements. This
adapter fetches the index and creates one PropertyRecord per
California announcement so the operator has a verifiable lead even when
structured size/address data is not embedded in the index page.
"""
from __future__ import annotations

import logging
import re
from typing import List

from bs4 import BeautifulSoup

from .base import BaseAdapter
from ..models import PropertyRecord

log = logging.getLogger(__name__)


SBA_AUCTION_URLS = [
    # Primary GovDeals collateral disposal storefront for SBA. Public list.
    "https://www.govdeals.com/index.cfm?fa=Main.AdvSearchResultsNew&searchPg=Advanced&kWord_all=retail&type=2&sortBy=ad&sortDir=1",
]


class SBAOREOAdapter(BaseAdapter):
    name = "sba_oreo"

    def fetch(self) -> List[PropertyRecord]:
        records: List[PropertyRecord] = []
        for url in SBA_AUCTION_URLS:
            resp = self.http.get(url)
            if not resp:
                continue
            records.extend(self._parse(resp.text, url))
        self._log_count(records)
        return records

    def _parse(self, html: str, source_url: str) -> List[PropertyRecord]:
        soup = BeautifulSoup(html, "html.parser")
        out: List[PropertyRecord] = []
        for row in soup.select("tr, div.search-result, li"):
            text = row.get_text(" ", strip=True)
            if not text or not re.search(r"retail|store|commercial", text, re.I):
                continue
            link = row.find("a", href=True)
            url = link["href"] if link else source_url
            state = self._state(text)
            if state and self.config.states and state not in self.config.states:
                continue

            out.append(PropertyRecord(
                property_name=(link.get_text() or "").strip() if link else None,
                state=state,
                property_type="Retail",
                status="Government Disposal Auction",
                off_market_signal="government_auction",
                source_name=self.name,
                source_url=url,
                notes="Posted on a government surplus / collateral disposal platform.",
            ))
        return out

    @staticmethod
    def _state(text: str) -> str | None:
        m = re.search(r"\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|"
                      r"MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|"
                      r"UT|VT|VA|WA|WV|WI|WY)\b", text)
        return m.group(1) if m else None
