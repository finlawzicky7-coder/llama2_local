"""Data models for retail property records."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class PropertyRecord:
    """A single retail property candidate.

    Field set is the union of what the task spec asks for. All textual
    fields default to None so adapters can populate only what they know.
    """

    # Identity
    property_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    apn: Optional[str] = None  # parcel number, used for dedupe

    # Classification
    property_type: Optional[str] = None        # e.g. "Retail"
    retail_subtype: Optional[str] = None       # e.g. "Strip Center", "Single Tenant"

    # Sizing
    total_sqft: Optional[float] = None
    available_sqft: Optional[float] = None
    lot_size_sqft: Optional[float] = None

    # Status
    status: Optional[str] = None               # e.g. "Tax Defaulted", "FDIC OREO", "Withdrawn"
    off_market_signal: Optional[str] = None    # short tag describing the off-market reason

    # Provenance
    source_url: Optional[str] = None
    source_name: Optional[str] = None

    # Public contact info (only if shown publicly)
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

    # Pricing
    asking_price: Optional[float] = None
    lease_rate: Optional[str] = None

    # Analyst notes
    notes: Optional[str] = None
    confidence_score: float = 0.0              # 0..1, off-market likelihood
    completeness_score: float = 0.0            # 0..1, data completeness

    # Timestamp
    captured_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> dict:
        return asdict(self)

    def dedupe_key(self) -> str:
        """Stable key used to drop duplicates across sources."""
        if self.apn:
            return f"apn:{self.apn.strip().lower()}"
        if self.address and self.city and self.state:
            normalized = f"{self.address}|{self.city}|{self.state}".lower()
            return f"addr:{' '.join(normalized.split())}"
        if self.property_name and self.city:
            return f"name:{self.property_name.strip().lower()}|{self.city.strip().lower()}"
        return f"src:{self.source_name}|{self.source_url}"


@dataclass
class RejectedCandidate:
    """A property that was filtered out, with the reason."""
    record: PropertyRecord
    reason: str
