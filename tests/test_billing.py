import json


def test_stripe_webhook_records_event(client, bundle):
    payload = json.dumps({"type": "customer.subscription.created", "data": {"id": "sub_1"}}).encode("utf-8")
    r = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"Stripe-Signature": "whsec_test", "Content-Type": "application/json"},
    )
    assert r.status_code == 200
    kinds = [e["kind"] for e in bundle.events.events]
    assert "stripe.customer.subscription.created" in kinds


def test_stripe_webhook_rejects_bad_signature(client, bundle):
    r = client.post(
        "/webhooks/stripe",
        content=b'{"type":"x"}',
        headers={"Stripe-Signature": "wrong", "Content-Type": "application/json"},
    )
    assert r.status_code == 400


def test_stripe_records_booking_usage_via_port(bundle):
    import asyncio
    from app.types import Booking
    from datetime import datetime, timezone
    from app.billing import record_booking_usage

    booking = Booking(
        id="b1", tenant_id="t1", customer_id="c1",
        scheduled_for=datetime(2026, 5, 1, 14, 0, tzinfo=timezone.utc),
    )
    rec_id = asyncio.run(record_booking_usage(bundle.stripe, "t1", "cus_123", booking))
    assert rec_id and rec_id.startswith("sur_")
    assert bundle.stripe.usage_records == [{"tenant_id": "t1", "stripe_customer_id": "cus_123", "qty": 1}]


def test_stripe_records_booking_usage_skips_when_no_customer(bundle):
    import asyncio
    from app.types import Booking
    from datetime import datetime, timezone
    from app.billing import record_booking_usage

    booking = Booking(id="b1", tenant_id="t1", customer_id="c1",
                      scheduled_for=datetime(2026, 5, 1, 14, 0, tzinfo=timezone.utc))
    assert asyncio.run(record_booking_usage(bundle.stripe, "t1", None, booking)) is None
    assert bundle.stripe.usage_records == []
