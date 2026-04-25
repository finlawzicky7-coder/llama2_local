import asyncio
from datetime import datetime, timedelta, timezone

from app.digest import build_digest, render_email, FakeEmail
from app.types import Booking, Call


def test_build_digest_counts(tenant):
    now = datetime.now(timezone.utc)
    calls = [
        Call(id="1", tenant_id=tenant.id, twilio_call_sid="a", from_e164="+1", to_e164="+2",
             started_at=now, status="completed"),
        Call(id="2", tenant_id=tenant.id, twilio_call_sid="b", from_e164="+1", to_e164="+2",
             started_at=now, status="emergency_routed"),
        Call(id="3", tenant_id=tenant.id, twilio_call_sid="c", from_e164="+1", to_e164="+2",
             started_at=now, status="lost"),
    ]
    bookings = [
        Booking(id="b1", tenant_id=tenant.id, customer_id="c1", scheduled_for=now),
    ]
    d = asyncio.run(build_digest(tenant, calls, bookings, now - timedelta(days=1), now))
    assert d.calls_total == 3
    assert d.calls_answered == 1
    assert d.calls_emergency_routed == 1
    assert d.bookings_total == 1


def test_render_email_includes_counts(tenant):
    from app.digest import DigestPayload
    now = datetime.now(timezone.utc)
    d = DigestPayload(
        tenant_id=tenant.id, period_start=now - timedelta(days=1), period_end=now,
        calls_total=10, calls_answered=7, calls_emergency_routed=1, bookings_total=3,
    )
    subject, body = render_email(tenant, d)
    assert "3 bookings" in subject
    assert "Calls received: 10" in body
    assert "Bookings created: 3" in body


def test_fake_email_records_send():
    em = FakeEmail()
    msg_id = asyncio.run(em.send("owner@example.com", "subject", "body"))
    assert msg_id.startswith("em_")
    assert em.sent == [{"to": "owner@example.com", "subject": "subject", "body": "body", "id": msg_id}]
