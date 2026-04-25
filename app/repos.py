"""Repository interfaces + an in-memory implementation used in tests.

Production uses the asyncpg-backed implementation in `app.db.pg`.
Tests inject the in-memory one to keep them offline.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional, Protocol

from app.types import Booking, Call, Customer, Slot, Tenant


class TenantRepo(Protocol):
    async def get(self, tenant_id: str) -> Optional[Tenant]: ...
    async def get_by_e164(self, e164: str) -> Optional[Tenant]: ...


class CallRepo(Protocol):
    async def create(self, call: Call) -> Call: ...
    async def append_transcript(self, call_id: str, role: str, text: str) -> None: ...
    async def set_status(self, call_id: str, status: str) -> None: ...
    async def get(self, call_id: str) -> Optional[Call]: ...


class CustomerRepo(Protocol):
    async def upsert(self, tenant_id: str, phone_e164: str, name: Optional[str], address: Optional[str], zip: Optional[str]) -> Customer: ...
    async def get_by_phone(self, tenant_id: str, phone_e164: str) -> Optional[Customer]: ...


class BookingRepo(Protocol):
    async def create_idempotent(self, booking: Booking) -> tuple[Booking, bool]: ...
    async def list_recent(self, tenant_id: str, since: datetime) -> list[Booking]: ...


class CalendarPort(Protocol):
    async def lookup_open_slots(self, tenant_id: str, after: datetime, count: int) -> list[Slot]: ...
    async def create_event(self, tenant_id: str, booking: Booking) -> str: ...


class SmsPort(Protocol):
    async def send(self, tenant_id: str, to_e164: str, body: str) -> str: ...


class EventLog(Protocol):
    async def record(self, tenant_id: Optional[str], actor: str, kind: str, payload: dict) -> None: ...


# ─────────────────────────────────────────────────────────────────────
# In-memory implementations (offline tests + local dev)
# ─────────────────────────────────────────────────────────────────────


class InMemoryTenantRepo:
    def __init__(self, tenants: list[Tenant], number_to_tenant: dict[str, str]):
        self._by_id = {t.id: t for t in tenants}
        self._by_e164 = number_to_tenant

    async def get(self, tenant_id: str) -> Optional[Tenant]:
        return self._by_id.get(tenant_id)

    async def get_by_e164(self, e164: str) -> Optional[Tenant]:
        tid = self._by_e164.get(e164)
        return self._by_id.get(tid) if tid else None


class InMemoryCallRepo:
    def __init__(self) -> None:
        self._calls: dict[str, Call] = {}

    async def create(self, call: Call) -> Call:
        self._calls[call.id] = call
        return call

    async def append_transcript(self, call_id: str, role: str, text: str) -> None:
        c = self._calls[call_id]
        c.transcript.append({"role": role, "text": text, "at": datetime.now(timezone.utc).isoformat()})

    async def set_status(self, call_id: str, status: str) -> None:
        self._calls[call_id].status = status

    async def get(self, call_id: str) -> Optional[Call]:
        return self._calls.get(call_id)


class InMemoryCustomerRepo:
    def __init__(self) -> None:
        self._by_key: dict[tuple[str, str], Customer] = {}

    async def upsert(self, tenant_id, phone_e164, name, address, zip):
        key = (tenant_id, phone_e164)
        existing = self._by_key.get(key)
        if existing:
            existing.name = name or existing.name
            existing.address = address or existing.address
            existing.zip = zip or existing.zip
            return existing
        c = Customer(id=str(uuid.uuid4()), tenant_id=tenant_id, phone_e164=phone_e164,
                     name=name, address=address, zip=zip)
        self._by_key[key] = c
        return c

    async def get_by_phone(self, tenant_id, phone_e164):
        return self._by_key.get((tenant_id, phone_e164))


class InMemoryBookingRepo:
    def __init__(self) -> None:
        self._by_id: dict[str, Booking] = {}
        self._idem: dict[tuple[str, str, str], str] = {}  # (tenant, customer, sched) -> booking_id

    async def create_idempotent(self, booking: Booking) -> tuple[Booking, bool]:
        key = (booking.tenant_id, booking.customer_id,
               booking.scheduled_for.astimezone(timezone.utc).replace(second=0, microsecond=0).isoformat())
        existing_id = self._idem.get(key)
        if existing_id:
            return self._by_id[existing_id], False
        self._by_id[booking.id] = booking
        self._idem[key] = booking.id
        return booking, True

    async def list_recent(self, tenant_id: str, since: datetime) -> list[Booking]:
        return [b for b in self._by_id.values()
                if b.tenant_id == tenant_id and b.scheduled_for >= since]


class InMemoryEventLog:
    def __init__(self) -> None:
        self.events: list[dict] = []

    async def record(self, tenant_id, actor, kind, payload):
        self.events.append({"tenant_id": tenant_id, "actor": actor, "kind": kind, "payload": payload})


class FakeCalendar:
    """Returns deterministic open slots; records created events."""

    def __init__(self, base: datetime):
        self.base = base
        self.created: list[Booking] = []

    async def lookup_open_slots(self, tenant_id: str, after: datetime, count: int) -> list[Slot]:
        slots = []
        cur = after.replace(minute=0, second=0, microsecond=0)
        for i in range(count):
            cur = cur.replace(hour=10 + (i * 2) % 8)
            slots.append(Slot(start=cur, end=cur.replace(hour=cur.hour + 2)))
        return slots

    async def create_event(self, tenant_id: str, booking: Booking) -> str:
        self.created.append(booking)
        return f"gcal_evt_{booking.id[:8]}"


class FakeSms:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send(self, tenant_id: str, to_e164: str, body: str) -> str:
        sid = f"SM{len(self.sent):06d}"
        self.sent.append({"sid": sid, "tenant_id": tenant_id, "to": to_e164, "body": body})
        return sid
