"""asyncpg-backed repos.

Used in production. Tests use the in-memory implementations in
`app.repos`. We don't ship an integration test that talks to a real
Postgres on this branch — that's gated behind the optional
`RINGBACK_LIVE_DB_URL` env var (see `tests/integration/`).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

import asyncpg  # type: ignore

from app.types import Booking, Call, Customer, Tenant


class PgPool:
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        if not self._pool:
            self._pool = await asyncpg.create_pool(self._dsn, min_size=1, max_size=5)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    @property
    def pool(self) -> asyncpg.Pool:
        if not self._pool:
            raise RuntimeError("PgPool.connect() must be called first")
        return self._pool


class PgTenantRepo:
    def __init__(self, pool: PgPool):
        self._pool = pool

    async def get(self, tenant_id: str) -> Optional[Tenant]:
        async with self._pool.pool.acquire() as conn:
            row = await conn.fetchrow("select * from tenants where id = $1", tenant_id)
        return self._row_to_tenant(row) if row else None

    async def get_by_e164(self, e164: str) -> Optional[Tenant]:
        async with self._pool.pool.acquire() as conn:
            row = await conn.fetchrow(
                "select t.* from tenants t join phone_numbers p on p.tenant_id = t.id "
                "where p.e164 = $1 and p.status = 'active' limit 1",
                e164,
            )
        return self._row_to_tenant(row) if row else None

    @staticmethod
    def _row_to_tenant(row) -> Tenant:
        return Tenant(
            id=str(row["id"]),
            name=row["name"],
            brand=row["brand"],
            timezone=row["timezone"],
            locale=row["locale"],
            plan=row["plan"],
        )


class PgCallRepo:
    def __init__(self, pool: PgPool):
        self._pool = pool

    async def create(self, call: Call) -> Call:
        async with self._pool.pool.acquire() as conn:
            await conn.execute(
                "insert into calls (id, tenant_id, twilio_call_sid, from_e164, to_e164, started_at, status) "
                "values ($1,$2,$3,$4,$5,$6,$7)",
                call.id, call.tenant_id, call.twilio_call_sid,
                call.from_e164, call.to_e164, call.started_at, call.status,
            )
        return call

    async def append_transcript(self, call_id: str, role: str, text: str) -> None:
        entry = json.dumps({"role": role, "text": text, "at": datetime.now(timezone.utc).isoformat()})
        async with self._pool.pool.acquire() as conn:
            await conn.execute(
                "update calls set transcript_jsonb = transcript_jsonb || $2::jsonb where id = $1",
                call_id, f"[{entry}]",
            )

    async def set_status(self, call_id: str, status: str) -> None:
        async with self._pool.pool.acquire() as conn:
            await conn.execute("update calls set status = $2 where id = $1", call_id, status)

    async def get(self, call_id: str) -> Optional[Call]:
        async with self._pool.pool.acquire() as conn:
            row = await conn.fetchrow("select * from calls where id = $1", call_id)
        if not row:
            return None
        return Call(
            id=str(row["id"]),
            tenant_id=str(row["tenant_id"]),
            twilio_call_sid=row["twilio_call_sid"],
            from_e164=row["from_e164"],
            to_e164=row["to_e164"],
            started_at=row["started_at"],
            status=row["status"],
        )


class PgCustomerRepo:
    def __init__(self, pool: PgPool):
        self._pool = pool

    async def upsert(self, tenant_id, phone_e164, name, address, zip):
        async with self._pool.pool.acquire() as conn:
            row = await conn.fetchrow(
                "insert into customers (tenant_id, phone_e164, name, address, zip) "
                "values ($1,$2,$3,$4,$5) "
                "on conflict (tenant_id, phone_e164) do update set "
                "  name = coalesce(excluded.name, customers.name), "
                "  address = coalesce(excluded.address, customers.address), "
                "  zip = coalesce(excluded.zip, customers.zip) "
                "returning *",
                tenant_id, phone_e164, name, address, zip,
            )
        return Customer(
            id=str(row["id"]), tenant_id=str(row["tenant_id"]),
            phone_e164=row["phone_e164"], name=row["name"],
            address=row["address"], zip=row["zip"],
        )

    async def get_by_phone(self, tenant_id, phone_e164):
        async with self._pool.pool.acquire() as conn:
            row = await conn.fetchrow(
                "select * from customers where tenant_id = $1 and phone_e164 = $2",
                tenant_id, phone_e164,
            )
        if not row:
            return None
        return Customer(
            id=str(row["id"]), tenant_id=str(row["tenant_id"]),
            phone_e164=row["phone_e164"], name=row["name"],
            address=row["address"], zip=row["zip"],
        )


class PgBookingRepo:
    def __init__(self, pool: PgPool):
        self._pool = pool

    async def create_idempotent(self, booking: Booking) -> tuple[Booking, bool]:
        async with self._pool.pool.acquire() as conn:
            existing = await conn.fetchrow(
                "select * from bookings where tenant_id = $1 and customer_id = $2 and scheduled_for = $3",
                booking.tenant_id, booking.customer_id, booking.scheduled_for,
            )
            if existing:
                return self._row_to_booking(existing), False
            row = await conn.fetchrow(
                "insert into bookings (id, tenant_id, customer_id, scheduled_for, duration_minutes, status, notes) "
                "values ($1,$2,$3,$4,$5,$6,$7) returning *",
                booking.id, booking.tenant_id, booking.customer_id,
                booking.scheduled_for, booking.duration_minutes, booking.status, booking.notes,
            )
            return self._row_to_booking(row), True

    async def list_recent(self, tenant_id, since):
        async with self._pool.pool.acquire() as conn:
            rows = await conn.fetch(
                "select * from bookings where tenant_id = $1 and scheduled_for >= $2 order by scheduled_for",
                tenant_id, since,
            )
        return [self._row_to_booking(r) for r in rows]

    @staticmethod
    def _row_to_booking(row) -> Booking:
        return Booking(
            id=str(row["id"]), tenant_id=str(row["tenant_id"]),
            customer_id=str(row["customer_id"]), scheduled_for=row["scheduled_for"],
            duration_minutes=row["duration_minutes"], status=row["status"],
            gcal_event_id=row.get("gcal_event_id") if hasattr(row, "get") else row["gcal_event_id"],
            notes=row["notes"],
        )


class PgEventLog:
    def __init__(self, pool: PgPool):
        self._pool = pool

    async def record(self, tenant_id, actor, kind, payload):
        async with self._pool.pool.acquire() as conn:
            await conn.execute(
                "insert into events (tenant_id, actor, kind, payload_jsonb) values ($1,$2,$3,$4)",
                tenant_id, actor, kind, json.dumps(payload),
            )
