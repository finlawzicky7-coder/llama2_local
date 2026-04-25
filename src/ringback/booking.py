"""Booking model and idempotent booking-key derivation.

The Ringback agent must avoid double-booking when an SMS arrives twice
or a webhook is replayed. We enforce idempotency two ways:

    1. Database constraint: `bookings (tenant_id, customer_id, scheduled_for)`
       is UNIQUE (see `supabase/schema.sql`).
    2. Application-level idempotency key (`booking_key`) used by the
       `create_booking` tool to detect retries before they hit the DB.

This module is pure-Python, no DB calls — it's just the math.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class BookingRequest:
    tenant_id: str
    customer_phone_e164: str
    job_type_label: str
    scheduled_for: datetime  # must be timezone-aware

    def __post_init__(self) -> None:
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self._looks_like_e164(self.customer_phone_e164):
            raise ValueError(f"customer_phone_e164 must be E.164: {self.customer_phone_e164!r}")
        if not self.job_type_label:
            raise ValueError("job_type_label is required")
        if self.scheduled_for.tzinfo is None:
            raise ValueError("scheduled_for must be timezone-aware")

    @staticmethod
    def _looks_like_e164(value: str) -> bool:
        return bool(re.fullmatch(r"\+[1-9]\d{6,14}", value or ""))


def booking_key(req: BookingRequest) -> str:
    """Stable idempotency key for a booking request.

    Two callers with the same tenant, phone, and scheduled_for (rounded
    to the minute) produce the same key. Time is normalized to UTC.
    """
    sched_utc = req.scheduled_for.astimezone(timezone.utc).replace(second=0, microsecond=0)
    raw = "|".join(
        [
            req.tenant_id,
            req.customer_phone_e164,
            sched_utc.isoformat(),
        ]
    )
    return "bk_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
