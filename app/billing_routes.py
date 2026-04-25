"""Stripe webhook + minimal admin/billing endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.deps import RuntimeBundle, get_runtime

router = APIRouter()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, bundle: RuntimeBundle = Depends(get_runtime)) -> dict:
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        event = bundle.stripe.construct_event(payload, sig)
    except Exception as e:  # bad signature or malformed
        raise HTTPException(status_code=400, detail=f"invalid stripe event: {e}")
    kind = event.get("type") or event.get("kind") or "unknown"
    await bundle.events.record(None, "system", f"stripe.{kind}", event)
    return {"received": True}
