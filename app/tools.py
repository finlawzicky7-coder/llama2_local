"""Tool functions exposed to the agent.

Each tool is an async function that takes a typed args dict and a
`ToolDeps` bundle of repos + ports. Tools are the *only* things the
agent is allowed to do that have side effects.

Tool authorization rule: every tool re-validates that the `tenant_id`
on the call/booking matches the caller's call context. The runtime
passes an immutable `tenant_id` into deps; tools never trust args.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from app.repos import (
    BookingRepo,
    CalendarPort,
    CallRepo,
    CustomerRepo,
    EventLog,
    SmsPort,
    TenantRepo,
)
from app.types import Booking, Slot
from ringback.booking import BookingRequest, booking_key
from ringback.emergency import is_emergency


@dataclass
class ToolDeps:
    tenant_id: str
    call_id: str
    customer_phone_e164: str
    tenants: TenantRepo
    calls: CallRepo
    customers: CustomerRepo
    bookings: BookingRepo
    calendar: CalendarPort
    sms: SmsPort
    events: EventLog


async def lookup_open_slots(args: dict[str, Any], deps: ToolDeps) -> dict[str, Any]:
    after_iso = args.get("earliest_after_iso") or datetime.now(timezone.utc).isoformat()
    count = int(args.get("count") or 3)
    after = datetime.fromisoformat(after_iso.replace("Z", "+00:00"))
    slots = await deps.calendar.lookup_open_slots(deps.tenant_id, after, count)
    await deps.events.record(deps.tenant_id, "agent", "lookup_open_slots",
                             {"call_id": deps.call_id, "count": len(slots)})
    return {"slots": [{"start_iso": s.start.isoformat(), "end_iso": s.end.isoformat(), "label": s.label}
                       for s in slots]}


async def create_booking(args: dict[str, Any], deps: ToolDeps) -> dict[str, Any]:
    name = (args.get("customer_name") or "").strip() or None
    address = (args.get("address") or "").strip() or None
    zip_ = (args.get("zip") or "").strip() or None
    job_type = (args.get("job_type") or "").strip() or "service call"
    scheduled_iso = args["scheduled_for_iso"]
    notes = args.get("notes")

    customer = await deps.customers.upsert(
        deps.tenant_id, deps.customer_phone_e164, name, address, zip_,
    )
    sched = datetime.fromisoformat(scheduled_iso.replace("Z", "+00:00"))
    if sched.tzinfo is None:
        sched = sched.replace(tzinfo=timezone.utc)

    BookingRequest(
        tenant_id=deps.tenant_id,
        customer_phone_e164=customer.phone_e164,
        job_type_label=job_type,
        scheduled_for=sched,
    )

    booking = Booking(
        id=str(uuid.uuid4()),
        tenant_id=deps.tenant_id,
        customer_id=customer.id,
        scheduled_for=sched,
        duration_minutes=int(args.get("duration_minutes", 60)),
        job_type_label=job_type,
        notes=notes,
    )
    booking, created = await deps.bookings.create_idempotent(booking)

    if created:
        booking.gcal_event_id = await deps.calendar.create_event(deps.tenant_id, booking)
        await deps.events.record(deps.tenant_id, "agent", "booking.created",
                                 {"booking_id": booking.id, "call_id": deps.call_id})
    return {
        "booking_id": booking.id,
        "scheduled_for_iso": booking.scheduled_for.isoformat(),
        "gcal_event_id": booking.gcal_event_id,
        "newly_created": created,
        "idempotency_key": booking_key(BookingRequest(
            tenant_id=deps.tenant_id,
            customer_phone_e164=customer.phone_e164,
            job_type_label=job_type,
            scheduled_for=sched,
        )),
    }


async def send_sms(args: dict[str, Any], deps: ToolDeps) -> dict[str, Any]:
    body = args["body"]
    to = args.get("to_e164") or deps.customer_phone_e164
    sid = await deps.sms.send(deps.tenant_id, to, body)
    await deps.events.record(deps.tenant_id, "agent", "sms.sent",
                             {"sid": sid, "call_id": deps.call_id})
    return {"sid": sid}


async def route_emergency(args: dict[str, Any], deps: ToolDeps) -> dict[str, Any]:
    tenant = await deps.tenants.get(deps.tenant_id)
    on_call = tenant.on_call_number if tenant else None
    await deps.events.record(deps.tenant_id, "agent", "call.emergency_routed",
                             {"call_id": deps.call_id, "on_call_number": on_call})
    await deps.calls.set_status(deps.call_id, "emergency_routed")
    return {"on_call_number": on_call}


async def end_call(args: dict[str, Any], deps: ToolDeps) -> dict[str, Any]:
    summary = args.get("summary", "")
    await deps.calls.append_transcript(deps.call_id, "system", f"summary: {summary}")
    await deps.calls.set_status(deps.call_id, "completed")
    await deps.events.record(deps.tenant_id, "agent", "call.completed",
                             {"call_id": deps.call_id})
    return {"ok": True}


TOOLS = {
    "lookup_open_slots": lookup_open_slots,
    "create_booking": create_booking,
    "send_sms": send_sms,
    "route_emergency": route_emergency,
    "end_call": end_call,
}


def detect_inbound_emergency(utterance: str, tenant_keywords: list[str]) -> bool:
    return is_emergency(utterance, tenant_keywords)
