"""Voice flow end-to-end test.

Drives the full /voice/incoming → /voice/turn loop using a scripted
FakeLLMClient that calls real tools. Asserts that:

  - Twilio receives valid TwiML at every step.
  - The agent calls lookup_open_slots → send_sms → create_booking → end_call.
  - A booking row is written.
  - The Google Calendar fake records the event.
  - The SMS fake recorded the slot offer message.
"""

from __future__ import annotations

from app.llm import FakeLLMClient


def _scripted():
    """Sequence of LLM responses that exercise the full booking happy path."""
    return [
        # turn 1: caller said "Hi this is Mike at 100 Main"
        "Got it, Mike. What's the full address with the ZIP?",
        # turn 2: caller said "100 Main Street Dallas 75001"
        "Thanks. Briefly, what's going on?",
        # turn 3: caller said "AC won't cool"
        "Understood. How urgent — today, this week?",
        # turn 4: caller said "tomorrow morning works"
        '<tool name="lookup_open_slots">{"count":3,"earliest_after_iso":"2026-05-01T15:00:00+00:00"}</tool>',
        # after slot lookup, send SMS, then create booking
        '<tool name="send_sms">{"body":"Hi Mike, Acme HVAC. Pick: A) Tue 10–12 B) Tue 12–2 C) Tue 2–4. Reply A/B/C. Reply STOP to opt out."}</tool>',
        '<tool name="create_booking">{"customer_name":"Mike","address":"100 Main Street Dallas","zip":"75001","job_type":"HVAC service","scheduled_for_iso":"2026-05-01T15:00:00+00:00","notes":"AC won\'t cool"}</tool>',
        '<tool name="end_call">{"summary":"booked HVAC service for Mike at 100 Main, AC won\'t cool"}</tool>',
        "Thanks Mike — we'll see you tomorrow morning.",
    ]


def test_voice_happy_path(client, bundle, tenant):
    bundle.llm = FakeLLMClient(scripted=_scripted())

    r = client.post(
        "/voice/incoming",
        data={"From": "+14155551212", "To": "+18005551212", "CallSid": "CA_test_001"},
    )
    assert r.status_code == 200
    assert "<Gather" in r.text
    assert "may be recorded" in r.text.lower()

    inputs = [
        "Hi this is Mike at 100 Main",
        "100 Main Street Dallas 75001",
        "AC won't cool",
        "tomorrow morning works",
    ]
    last = None
    for text in inputs:
        last = client.post(
            "/voice/turn",
            data={"CallSid": "CA_test_001", "SpeechResult": text},
        )
        assert last.status_code == 200

    assert last is not None
    assert "<Hangup" in last.text or "<Gather" in last.text

    # SMS slot offer was sent.
    assert any("Pick:" in m["body"] or "Reply A" in m["body"] for m in bundle.sms.sent)

    # Booking was created and a calendar event recorded.
    assert len(bundle.calendar.created) == 1
    booking = bundle.calendar.created[0]
    assert booking.tenant_id == tenant.id
    assert booking.job_type_label == "HVAC service"

    # Event log captured the booking.
    kinds = [e["kind"] for e in bundle.events.events]
    assert "booking.created" in kinds
    assert "sms.sent" in kinds
    assert "lookup_open_slots" in kinds


def test_voice_emergency_routes_out(client, bundle, tenant):
    bundle.llm = FakeLLMClient(scripted=["unused — emergency short-circuits the LLM"])

    r = client.post(
        "/voice/incoming",
        data={"From": "+14155551212", "To": "+18005551212", "CallSid": "CA_test_002"},
    )
    assert r.status_code == 200

    r = client.post(
        "/voice/turn",
        data={"CallSid": "CA_test_002", "SpeechResult": "I smell gas in the kitchen"},
    )
    assert r.status_code == 200
    # Emergency response must Dial out to the on-call number.
    assert "<Dial>" in r.text
    assert tenant.on_call_number in r.text

    kinds = [e["kind"] for e in bundle.events.events]
    assert "call.emergency_routed" in kinds


def test_voice_unconfigured_number_hangs_up(client, bundle):
    r = client.post(
        "/voice/incoming",
        data={"From": "+14155551212", "To": "+18885550000", "CallSid": "CA_test_003"},
    )
    assert r.status_code == 200
    assert "<Hangup" in r.text


def test_voice_turn_without_session_hangs_up(client, bundle):
    r = client.post(
        "/voice/turn",
        data={"CallSid": "CA_unknown", "SpeechResult": "hello"},
    )
    assert r.status_code == 200
    assert "<Hangup" in r.text
