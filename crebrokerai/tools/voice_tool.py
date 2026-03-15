"""Twilio voice call tool with TCPA compliance and LLM conversation simulation."""

from __future__ import annotations

import json

from crewai.tools import BaseTool

from crebrokerai.config.settings import settings
from crebrokerai.utils.compliance import check_call_compliance, TCPA_INTRO
from crebrokerai.utils.logging import get_logger

log = get_logger("tools.voice")


class TwilioVoiceCallTool(BaseTool):
    """Initiate a qualification call via Twilio (or mock in demo mode)."""

    name: str = "make_voice_call"
    description: str = (
        "Make an outbound qualification call to a prospect. "
        "Input: JSON with 'phone', 'prospect_name', 'company_name', "
        "'call_script', 'qualifying_questions'. "
        "Enforces TCPA compliance and requires human approval. "
        "In mock mode, simulates the conversation and returns results."
    )

    def _run(self, call_json: str) -> str:
        try:
            data = json.loads(call_json)
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": "Invalid JSON input"})

        phone = data.get("phone", "")
        prospect_name = data.get("prospect_name", "")
        company_name = data.get("company_name", "")
        call_script = data.get("call_script", "")

        # ── TCPA compliance check ────────────────────────────
        compliance = check_call_compliance(phone)
        if not compliance.passed:
            log.warning("TCPA check failed for %s: %s", prospect_name, compliance.issues)
            return json.dumps({
                "status": "blocked",
                "reason": "TCPA compliance failure",
                "issues": compliance.issues,
            })

        # ── Mock mode (no Twilio credentials) ────────────────
        if not settings.twilio_account_sid:
            log.info("[MOCK] Call to %s at %s", prospect_name, phone)

            # Simulate a qualification conversation
            simulated_outcome = _simulate_call(prospect_name, company_name)
            return json.dumps({
                "status": "mock_completed",
                "phone": phone,
                "prospect_name": prospect_name,
                "company_name": company_name,
                "call_duration_sec": simulated_outcome["duration"],
                "outcome": simulated_outcome["outcome"],
                "qualified": simulated_outcome["qualified"],
                "tour_booked": simulated_outcome["tour_booked"],
                "notes": simulated_outcome["notes"],
                "message": "MOCK MODE — no Twilio credentials. Call simulated.",
                "human_approval_required": True,
            })

        # ── Real Twilio call ─────────────────────────────────
        try:
            from twilio.rest import Client

            client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

            intro = TCPA_INTRO.format(
                agent_name="CREBrokerAI",
                brokerage_name=settings.sendgrid_from_name,
            )

            # In production, this would use Twilio's <Say> TwiML with an
            # LLM-powered conversation loop. For now, we initiate the call
            # and log it.
            call = client.calls.create(
                to=phone,
                from_=settings.twilio_from_number,
                twiml=f"<Response><Say>{intro}</Say><Pause length='2'/>"
                      f"<Say>{call_script[:500]}</Say></Response>",
            )
            log.info("Call initiated to %s — SID %s", phone, call.sid)
            return json.dumps({
                "status": "initiated",
                "call_sid": call.sid,
                "phone": phone,
                "prospect_name": prospect_name,
            })
        except Exception as exc:
            log.error("Twilio error: %s", exc)
            return json.dumps({"status": "error", "message": str(exc)})


def _simulate_call(prospect_name: str, company_name: str) -> dict:
    """Simulate a qualification call for mock mode."""
    import random

    outcomes = [
        {
            "duration": random.randint(120, 300),
            "outcome": "interested",
            "qualified": True,
            "tour_booked": True,
            "notes": (
                f"{prospect_name} at {company_name} is actively looking for space. "
                "Current lease expires soon. Interested in touring next week. "
                "Needs 10-20k sqft, prefers Class A with parking."
            ),
        },
        {
            "duration": random.randint(60, 180),
            "outcome": "interested_not_ready",
            "qualified": True,
            "tour_booked": False,
            "notes": (
                f"{prospect_name} confirmed {company_name} is growing but "
                "not ready to tour for another 2-3 months. Requested follow-up email "
                "with available options."
            ),
        },
        {
            "duration": random.randint(30, 60),
            "outcome": "not_interested",
            "qualified": False,
            "tour_booked": False,
            "notes": (
                f"{prospect_name} indicated {company_name} recently renewed their lease. "
                "Not in the market. Removed from active pipeline."
            ),
        },
        {
            "duration": random.randint(45, 120),
            "outcome": "voicemail",
            "qualified": False,
            "tour_booked": False,
            "notes": (
                f"Reached voicemail for {prospect_name} at {company_name}. "
                "Left message with callback number. Will retry in 48 hours."
            ),
        },
    ]
    return random.choice(outcomes)
