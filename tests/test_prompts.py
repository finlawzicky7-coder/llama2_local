import pytest

from ringback.prompts import (
    SMS_BOOKING_CONFIRMATION,
    SMS_HELP_RESPONSE,
    SMS_SLOT_OFFER_TEMPLATE,
    VOICE_EMERGENCY_HANDOFF,
    VOICE_GREETING_TEMPLATE,
    render,
)


def test_voice_greeting_includes_recording_disclosure():
    msg = render(VOICE_GREETING_TEMPLATE, brand="Acme HVAC", trade_lower="hvac")
    assert "may be recorded" in msg.lower()


def test_emergency_handoff_uses_brand():
    msg = render(VOICE_EMERGENCY_HANDOFF, brand="Acme HVAC")
    assert "Acme HVAC" in msg


def test_sms_slot_offer_includes_stop_keyword():
    msg = render(
        SMS_SLOT_OFFER_TEMPLATE,
        first_name="Mike",
        brand="Acme HVAC",
        job_type="AC service",
        slot_a_local="Tue 10–12",
        slot_b_local="Tue 2–4",
        slot_c_local="Wed 8–10",
    )
    assert "STOP" in msg
    assert "Tue 2–4" in msg


def test_sms_help_response_lists_emergency_number():
    msg = render(SMS_HELP_RESPONSE, brand="Acme HVAC", emergency_number="+15555550101")
    assert "+15555550101" in msg


def test_sms_booking_confirmation_uses_when():
    msg = render(
        SMS_BOOKING_CONFIRMATION,
        first_name="Mike",
        brand="Acme HVAC",
        when_local="Tue 2–4",
    )
    assert "Tue 2–4" in msg


def test_render_raises_on_missing_field():
    with pytest.raises(KeyError):
        render(VOICE_GREETING_TEMPLATE, brand="Acme HVAC")  # missing trade_lower
