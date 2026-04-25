"""Stripe billing integration: subscription webhook + booking-fee usage records."""

from __future__ import annotations

import logging
from typing import Any, Optional, Protocol

from app.types import Booking

log = logging.getLogger(__name__)


class StripePort(Protocol):
    async def post_booked_job_usage(self, tenant_id: str, customer_id: str, qty: int = 1) -> str: ...
    def construct_event(self, payload: bytes, sig_header: str) -> dict: ...


class FakeStripe:
    """In-memory Stripe used in tests."""

    def __init__(self, secret: str = "whsec_test"):
        self._secret = secret
        self.usage_records: list[dict] = []
        self.constructed: list[dict] = []

    async def post_booked_job_usage(self, tenant_id: str, customer_id: str, qty: int = 1) -> str:
        rec = {"tenant_id": tenant_id, "stripe_customer_id": customer_id, "qty": qty}
        self.usage_records.append(rec)
        return f"sur_{len(self.usage_records):06d}"

    def construct_event(self, payload: bytes, sig_header: str) -> dict:
        # In real Stripe, this verifies signature. Fake just parses JSON.
        import json as _json
        evt = _json.loads(payload.decode("utf-8"))
        if sig_header != self._secret and self._secret != "":
            raise ValueError("bad signature")
        self.constructed.append(evt)
        return evt


class HTTPStripe:
    """Real Stripe wrapper — requires `stripe` SDK + a secret key."""

    def __init__(self, secret_key: str, webhook_secret: str, meter_id: Optional[str]):
        if not secret_key:
            raise ValueError("STRIPE_SECRET_KEY is required for HTTPStripe")
        import stripe  # type: ignore
        stripe.api_key = secret_key
        self._stripe = stripe
        self._webhook_secret = webhook_secret
        self._meter_id = meter_id

    async def post_booked_job_usage(self, tenant_id: str, customer_id: str, qty: int = 1) -> str:
        # Stripe usage records are sync in their SDK; the await keeps the
        # interface uniform with the Fake.
        if not self._meter_id:
            log.warning("no meter id configured; usage record skipped for tenant %s", tenant_id)
            return ""
        evt = self._stripe.billing.MeterEvent.create(
            event_name=self._meter_id,
            payload={"value": str(qty), "stripe_customer_id": customer_id},
        )
        return getattr(evt, "id", "") or ""

    def construct_event(self, payload: bytes, sig_header: str) -> dict:
        evt = self._stripe.Webhook.construct_event(payload, sig_header, self._webhook_secret)
        # Convert to dict (Stripe SDK returns a special object).
        return dict(evt)


async def record_booking_usage(stripe_client: StripePort, tenant_id: str, stripe_customer_id: Optional[str],
                                booking: Booking) -> Optional[str]:
    if not stripe_customer_id:
        log.info("tenant %s has no stripe customer; skipping usage record", tenant_id)
        return None
    return await stripe_client.post_booked_job_usage(tenant_id, stripe_customer_id, qty=1)
