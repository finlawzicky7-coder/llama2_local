"""Twilio voice + SMS webhook routes."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request, Response

from app.call_state import CallSession
from app.deps import RuntimeBundle, get_runtime
from app.runtime import run_turn
from app.tools import ToolDeps
from app.twiml import voice_dial, voice_say_and_gather, voice_say_and_hangup, sms_message
from app.twilio_deps import verify_twilio_signature
from app.types import Call

router = APIRouter()


@router.post("/voice/incoming")
async def voice_incoming(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    CallSid: str = Form(...),
    bundle: RuntimeBundle = Depends(get_runtime),
    _sig: None = Depends(verify_twilio_signature),
) -> Response:
    tenant = await bundle.tenants.get_by_e164(To)
    if not tenant:
        return Response(
            content=voice_say_and_hangup("This line is not configured. Please call back later."),
            media_type="application/xml",
        )

    call = await bundle.calls.create(Call(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        twilio_call_sid=CallSid,
        from_e164=From,
        to_e164=To,
        started_at=datetime.now(timezone.utc),
    ))
    session = CallSession(
        call_id=call.id,
        tenant_id=tenant.id,
        twilio_call_sid=CallSid,
        from_e164=From,
        to_e164=To,
    )
    bundle.call_state.put(session)

    greeting = (
        f"Thanks for calling {tenant.brand}. This is the after-hours assistant — "
        f"this call may be recorded for quality and scheduling. "
        f"What's your name and the address you need help at?"
    )
    return Response(
        content=voice_say_and_gather(f"{request.base_url}voice/turn", greeting),
        media_type="application/xml",
    )


@router.post("/voice/turn")
async def voice_turn(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: str = Form(""),
    bundle: RuntimeBundle = Depends(get_runtime),
    _sig: None = Depends(verify_twilio_signature),
) -> Response:
    session = bundle.call_state.get(CallSid)
    if not session:
        return Response(
            content=voice_say_and_hangup("Sorry, we lost the thread. We'll text to follow up."),
            media_type="application/xml",
        )
    tenant = await bundle.tenants.get(session.tenant_id)
    if not tenant:
        return Response(content=voice_say_and_hangup("Configuration error."), media_type="application/xml")

    deps = ToolDeps(
        tenant_id=session.tenant_id,
        call_id=session.call_id,
        customer_phone_e164=session.from_e164,
        tenants=bundle.tenants,
        calls=bundle.calls,
        customers=bundle.customers,
        bookings=bundle.bookings,
        calendar=bundle.calendar,
        sms=bundle.sms,
        events=bundle.events,
    )
    result = await run_turn(
        tenant=tenant,
        state=session.state,
        ctx=session.ctx,
        utterance=SpeechResult or "",
        history=session.history,
        llm=bundle.llm,
        deps=deps,
    )
    session.state = result.state
    bundle.call_state.put(session)

    if result.terminal:
        # Emergency: dial out. Otherwise: thank-you + hangup.
        if result.state.name == "ROUTED_EMERGENCY" and tenant.on_call_number:
            return Response(
                content=voice_dial(tenant.on_call_number, result.reply_text),
                media_type="application/xml",
            )
        bundle.call_state.delete(CallSid)
        return Response(
            content=voice_say_and_hangup(result.reply_text or "Thanks — we'll be in touch by text."),
            media_type="application/xml",
        )

    return Response(
        content=voice_say_and_gather(f"{request.base_url}voice/turn", result.reply_text or "Could you say that again?"),
        media_type="application/xml",
    )


@router.post("/sms/incoming")
async def sms_incoming(
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(""),
    MessageSid: str = Form(...),
    bundle: RuntimeBundle = Depends(get_runtime),
    _sig: None = Depends(verify_twilio_signature),
) -> Response:
    tenant = await bundle.tenants.get_by_e164(To)
    if not tenant:
        return Response(content=sms_message("This number is not configured."), media_type="application/xml")

    body = (Body or "").strip()
    upper = body.upper()
    if upper in {"STOP", "STOPALL", "UNSUBSCRIBE", "CANCEL", "QUIT"}:
        return Response(
            content=sms_message(f"{tenant.brand}: You won't receive further messages. Reply HELP for help."),
            media_type="application/xml",
        )
    if upper == "HELP":
        return Response(
            content=sms_message(f"{tenant.brand}: We answer inbound calls and book service. Reply STOP to opt out."),
            media_type="application/xml",
        )

    # SMS-only path: get-or-create a session keyed by phone+number for last 24h.
    pseudo_sid = f"SMS-{From}-{To}"
    session = bundle.call_state.get(pseudo_sid)
    if not session:
        call = await bundle.calls.create(Call(
            id=str(uuid.uuid4()),
            tenant_id=tenant.id,
            twilio_call_sid=pseudo_sid,
            from_e164=From,
            to_e164=To,
            started_at=datetime.now(timezone.utc),
        ))
        session = CallSession(
            call_id=call.id, tenant_id=tenant.id,
            twilio_call_sid=pseudo_sid, from_e164=From, to_e164=To,
        )
        bundle.call_state.put(session)

    deps = ToolDeps(
        tenant_id=session.tenant_id,
        call_id=session.call_id,
        customer_phone_e164=session.from_e164,
        tenants=bundle.tenants,
        calls=bundle.calls,
        customers=bundle.customers,
        bookings=bundle.bookings,
        calendar=bundle.calendar,
        sms=bundle.sms,
        events=bundle.events,
    )
    result = await run_turn(
        tenant=tenant, state=session.state, ctx=session.ctx,
        utterance=body, history=session.history, llm=bundle.llm, deps=deps,
    )
    session.state = result.state
    bundle.call_state.put(session)

    return Response(
        content=sms_message(result.reply_text or "Got it — what's the address and the issue?"),
        media_type="application/xml",
    )
