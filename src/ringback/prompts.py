"""Voice / SMS agent prompt templates.

These templates are the canonical scripts loaded by the agent runtime.
Tenant-specific values (brand, hours, etc.) are interpolated at runtime.

We do NOT inline tenant data in test snapshots — these are pure templates.

The greeting always includes a recording disclosure to satisfy two-party
consent jurisdictions (see `docs/market-research.md` §8 and SOP-6 in
`docs/operations-sop.md`).
"""

from __future__ import annotations

VOICE_GREETING_TEMPLATE = (
    "Thanks for calling {brand}. This is the after-hours assistant — "
    "this call may be recorded for quality and scheduling. "
    "I can help you book a time with one of our {trade_lower} techs. "
    "What's your name and the address you need help at?"
)

VOICE_EMERGENCY_HANDOFF = (
    "That sounds urgent. I'm transferring you to {brand}'s on-call line right now — "
    "stay on the line."
)

SMS_SLOT_OFFER_TEMPLATE = (
    "Hi {first_name}, this is {brand}. Earliest times for your {job_type}:\n"
    "A) {slot_a_local}\n"
    "B) {slot_b_local}\n"
    "C) {slot_c_local}\n"
    "Reply A, B, or C to confirm. Reply STOP to opt out."
)

SMS_BOOKING_CONFIRMATION = (
    "You're booked, {first_name}. {brand} will arrive {when_local}. "
    "Reply HELP for help, STOP to opt out."
)

SMS_HELP_RESPONSE = (
    "{brand}: We answer inbound calls and book service appointments. "
    "Reply STOP to stop messages. For emergencies call {emergency_number}."
)


def render(template: str, **fields: str) -> str:
    """Render a template, raising on missing keys (no silent defaults)."""
    return template.format(**fields)
