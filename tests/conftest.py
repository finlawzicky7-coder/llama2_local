"""Shared fixtures for app-level tests.

Each test gets a fresh in-memory bundle wired into `app.state.bundle`,
plus a known tenant + Twilio number → tenant mapping. Twilio signature
verification is bypassed via `SKIP_TWILIO_SIGNATURE=1`.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("SKIP_TWILIO_SIGNATURE", "1")

from app.config import reset_settings_for_test  # noqa: E402
from app.deps import RuntimeBundle  # noqa: E402
from app.llm import FakeLLMClient  # noqa: E402
from app.main import create_app  # noqa: E402
from app.repos import (  # noqa: E402
    FakeCalendar,
    FakeSms,
    InMemoryBookingRepo,
    InMemoryCallRepo,
    InMemoryCustomerRepo,
    InMemoryEventLog,
    InMemoryTenantRepo,
)
from app.billing import FakeStripe  # noqa: E402
from app.call_state import InMemoryCallStateStore  # noqa: E402
from app.digest import FakeEmail  # noqa: E402
from app.types import Tenant  # noqa: E402

from datetime import datetime, timezone  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_settings():
    reset_settings_for_test()
    yield
    reset_settings_for_test()


@pytest.fixture
def tenant() -> Tenant:
    return Tenant(
        id="11111111-1111-1111-1111-111111111111",
        name="Acme HVAC",
        brand="Acme HVAC",
        timezone="America/Chicago",
        locale="en-US",
        plan="tier_1",
        on_call_number="+15555550911",
        emergency_keywords=["no heat in winter"],
        job_types=["HVAC service"],
    )


@pytest.fixture
def bundle(tenant) -> RuntimeBundle:
    return RuntimeBundle(
        tenants=InMemoryTenantRepo(tenants=[tenant], number_to_tenant={"+18005551212": tenant.id}),
        calls=InMemoryCallRepo(),
        customers=InMemoryCustomerRepo(),
        bookings=InMemoryBookingRepo(),
        calendar=FakeCalendar(base=datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc)),
        sms=FakeSms(),
        events=InMemoryEventLog(),
        llm=FakeLLMClient(scripted=[]),
        email=FakeEmail(),
        stripe=FakeStripe(secret="whsec_test"),
        call_state=InMemoryCallStateStore(),
    )


@pytest.fixture
def client(bundle) -> TestClient:
    app = create_app()
    app.state.bundle = bundle
    return TestClient(app)
