"""Daily-digest builder.

Builds a summary for one tenant for the period [period_start, period_end)
out of `calls` + `bookings` + `events`. The dispatcher (separate module)
sends it via the email port.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from app.repos import BookingRepo, CallRepo
from app.types import Tenant


@dataclass
class DigestPayload:
    tenant_id: str
    period_start: datetime
    period_end: datetime
    calls_total: int
    calls_answered: int
    calls_emergency_routed: int
    bookings_total: int


class EmailPort(Protocol):
    async def send(self, to: str, subject: str, body: str) -> str: ...


class FakeEmail:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send(self, to: str, subject: str, body: str) -> str:
        msg_id = f"em_{len(self.sent):06d}"
        self.sent.append({"to": to, "subject": subject, "body": body, "id": msg_id})
        return msg_id


async def build_digest(
    tenant: Tenant,
    calls: list,
    bookings: list,
    period_start: datetime,
    period_end: datetime,
) -> DigestPayload:
    answered = sum(1 for c in calls if getattr(c, "status", "") in {"answered", "qualified", "completed"})
    emerg = sum(1 for c in calls if getattr(c, "status", "") == "emergency_routed")
    return DigestPayload(
        tenant_id=tenant.id,
        period_start=period_start,
        period_end=period_end,
        calls_total=len(calls),
        calls_answered=answered,
        calls_emergency_routed=emerg,
        bookings_total=len(bookings),
    )


def render_email(tenant: Tenant, d: DigestPayload) -> tuple[str, str]:
    subject = f"{tenant.brand} — yesterday: {d.bookings_total} bookings, {d.calls_total} calls"
    body = (
        f"Hi {tenant.brand},\n\n"
        f"Yesterday ({d.period_start:%a %b %d}):\n"
        f"  Calls received: {d.calls_total}\n"
        f"  Answered by Ringback: {d.calls_answered}\n"
        f"  Emergency-routed: {d.calls_emergency_routed}\n"
        f"  Bookings created: {d.bookings_total}\n\n"
        "Reply to this email if anything looks off.\n"
        "— Ringback"
    )
    return subject, body
