"""TCPA / CAN-SPAM compliance helpers.

All outbound communications MUST pass through these checks before sending.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ── CAN-SPAM required footer ────────────────────────────────────────────────
CAN_SPAM_FOOTER = """
---
You are receiving this email because we identified your company as a potential
match for available commercial space. If you no longer wish to receive these
messages, reply STOP or click here to unsubscribe: {unsubscribe_url}

{sender_name} | {sender_address}
This message is a commercial advertisement.
""".strip()


# ── TCPA consent phrases for voice ──────────────────────────────────────────
TCPA_INTRO = (
    "Hi, this is {agent_name} from {brokerage_name}. "
    "I'm calling regarding commercial office space opportunities. "
    "Do you have a moment to speak? You can ask me to stop at any time "
    "and I will remove you from our list immediately."
)


@dataclass
class ComplianceResult:
    passed: bool
    issues: list[str]


def check_email_compliance(
    subject: str,
    body: str,
    from_email: str,
) -> ComplianceResult:
    """Validate an outbound email for CAN-SPAM compliance."""
    issues: list[str] = []

    if not subject.strip():
        issues.append("Subject line is empty.")
    if "unsubscribe" not in body.lower() and "opt out" not in body.lower() and "stop" not in body.lower():
        issues.append("Email body must contain an unsubscribe / opt-out mechanism.")
    if not from_email or "@" not in from_email:
        issues.append("Valid From address is required.")
    if re.search(r"(guaranteed|act now|limited time|click below)", body, re.IGNORECASE):
        issues.append("Body contains potentially misleading phrases flagged by spam filters.")

    return ComplianceResult(passed=len(issues) == 0, issues=issues)


def check_call_compliance(phone: str) -> ComplianceResult:
    """Basic TCPA checks before an outbound call."""
    issues: list[str] = []

    if not phone or len(phone) < 10:
        issues.append("Invalid phone number.")
    # Placeholder: in production, check DNC registry here
    return ComplianceResult(passed=len(issues) == 0, issues=issues)


def append_can_spam_footer(
    body: str,
    sender_name: str = "CREBrokerAI",
    sender_address: str = "123 Main St, Suite 100, Austin TX 78701",
    unsubscribe_url: str = "https://yourbrokerage.com/unsubscribe",
) -> str:
    """Append CAN-SPAM compliant footer to an email body."""
    footer = CAN_SPAM_FOOTER.format(
        unsubscribe_url=unsubscribe_url,
        sender_name=sender_name,
        sender_address=sender_address,
    )
    return f"{body}\n\n{footer}"
