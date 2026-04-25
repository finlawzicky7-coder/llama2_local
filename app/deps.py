"""Runtime dependency wiring.

A `RuntimeBundle` holds every port + repo + LLM + state store the
route handlers need. The default `get_runtime()` returns the
production wiring; tests override it via FastAPI's
`app.dependency_overrides`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Request

from app.billing import FakeStripe, HTTPStripe, StripePort
from app.call_state import InMemoryCallStateStore
from app.config import get_settings
from app.digest import EmailPort, FakeEmail
from app.llm import FakeLLMClient, HTTPLLMClient, LLMClient
from app.repos import (
    BookingRepo,
    CalendarPort,
    CallRepo,
    CustomerRepo,
    EventLog,
    FakeCalendar,
    FakeSms,
    InMemoryBookingRepo,
    InMemoryCallRepo,
    InMemoryCustomerRepo,
    InMemoryEventLog,
    InMemoryTenantRepo,
    SmsPort,
    TenantRepo,
)
from app.types import Tenant


@dataclass
class RuntimeBundle:
    tenants: TenantRepo
    calls: CallRepo
    customers: CustomerRepo
    bookings: BookingRepo
    calendar: CalendarPort
    sms: SmsPort
    events: EventLog
    llm: LLMClient
    email: EmailPort
    stripe: StripePort
    call_state: InMemoryCallStateStore


_default_bundle: Optional[RuntimeBundle] = None


def _build_default() -> RuntimeBundle:
    """Build a bundle that works without external creds.

    Production swaps in `app.db.Pg*` repos, `HTTPLLMClient`, real
    Stripe/Resend/GoogleCalendar via `set_runtime_bundle()`.
    """
    settings = get_settings()
    tenants = InMemoryTenantRepo(tenants=[], number_to_tenant={})
    calls = InMemoryCallRepo()
    customers = InMemoryCustomerRepo()
    bookings = InMemoryBookingRepo()
    from datetime import datetime, timezone
    calendar = FakeCalendar(base=datetime.now(timezone.utc))
    sms = FakeSms()
    events = InMemoryEventLog()

    if settings.llm_provider == "http" and settings.llm_base_url and settings.llm_api_key and settings.llm_model:
        llm: LLMClient = HTTPLLMClient(settings.llm_base_url, settings.llm_api_key, settings.llm_model)
    else:
        llm = FakeLLMClient(scripted=[])

    email: EmailPort = FakeEmail()
    stripe: StripePort = FakeStripe(secret=settings.stripe_webhook_secret or "")
    if settings.stripe_secret_key:
        try:
            stripe = HTTPStripe(
                secret_key=settings.stripe_secret_key,
                webhook_secret=settings.stripe_webhook_secret or "",
                meter_id=settings.stripe_meter_booked_job,
            )
        except Exception:  # pragma: no cover
            pass

    return RuntimeBundle(
        tenants=tenants, calls=calls, customers=customers, bookings=bookings,
        calendar=calendar, sms=sms, events=events, llm=llm, email=email,
        stripe=stripe, call_state=InMemoryCallStateStore(),
    )


def set_runtime_bundle(bundle: RuntimeBundle) -> None:
    global _default_bundle
    _default_bundle = bundle


def get_runtime(request: Request) -> RuntimeBundle:
    # Allow per-app override via app.state.bundle (set by tests or main).
    bundle = getattr(request.app.state, "bundle", None)
    if bundle is not None:
        return bundle
    global _default_bundle
    if _default_bundle is None:
        _default_bundle = _build_default()
    return _default_bundle
