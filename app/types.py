"""Domain types shared across the runtime, repos, and tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Tenant:
    id: str
    name: str
    brand: str
    timezone: str
    locale: str
    plan: str
    on_call_number: Optional[str] = None
    emergency_keywords: list[str] = field(default_factory=list)
    job_types: list[str] = field(default_factory=list)


@dataclass
class Customer:
    id: str
    tenant_id: str
    phone_e164: str
    name: Optional[str] = None
    address: Optional[str] = None
    zip: Optional[str] = None


@dataclass
class Call:
    id: str
    tenant_id: str
    twilio_call_sid: str
    from_e164: str
    to_e164: str
    started_at: datetime
    status: str = "in_progress"
    transcript: list[dict] = field(default_factory=list)


@dataclass
class Booking:
    id: str
    tenant_id: str
    customer_id: str
    scheduled_for: datetime
    duration_minutes: int = 60
    job_type_label: Optional[str] = None
    status: str = "booked"
    gcal_event_id: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Slot:
    start: datetime
    end: datetime

    @property
    def label(self) -> str:
        # human-friendly local label, e.g. "Tue 10–12"
        return f"{self.start.strftime('%a %-I')}–{self.end.strftime('%-I')}"
