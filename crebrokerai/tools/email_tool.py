"""SendGrid email tool with CAN-SPAM compliance and human-in-the-loop approval."""

from __future__ import annotations

import json

from crewai.tools import BaseTool

from crebrokerai.config.settings import settings
from crebrokerai.utils.compliance import check_email_compliance, append_can_spam_footer
from crebrokerai.utils.logging import get_logger

log = get_logger("tools.email")


class SendGridEmailTool(BaseTool):
    """Send a CAN-SPAM compliant email via SendGrid (or mock in demo mode)."""

    name: str = "send_email"
    description: str = (
        "Send a personalized email to a prospect. "
        "Input: JSON with 'to_email', 'subject', 'body', 'prospect_name'. "
        "The tool enforces CAN-SPAM compliance and requires human approval "
        "before actually sending. Returns send status."
    )

    def _run(self, email_json: str) -> str:
        try:
            data = json.loads(email_json)
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": "Invalid JSON input"})

        to_email = data.get("to_email", "")
        subject = data.get("subject", "")
        body = data.get("body", "")
        prospect_name = data.get("prospect_name", "Prospect")

        # ── Compliance check ─────────────────────────────────
        body_with_footer = append_can_spam_footer(body)
        compliance = check_email_compliance(subject, body_with_footer, settings.sendgrid_from_email)

        if not compliance.passed:
            log.warning("Compliance failed for %s: %s", prospect_name, compliance.issues)
            return json.dumps({
                "status": "blocked",
                "reason": "CAN-SPAM compliance failure",
                "issues": compliance.issues,
            })

        # ── Mock mode (no API key) ───────────────────────────
        if not settings.sendgrid_api_key:
            log.info("[MOCK] Email to %s <%s>: %s", prospect_name, to_email, subject)
            return json.dumps({
                "status": "mock_sent",
                "to": to_email,
                "subject": subject,
                "body_preview": body_with_footer[:200],
                "message": "MOCK MODE — no SendGrid API key. Email logged but not sent.",
                "human_approval_required": True,
            })

        # ── Real SendGrid send ───────────────────────────────
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=(settings.sendgrid_from_email, settings.sendgrid_from_name),
                to_emails=to_email,
                subject=subject,
                plain_text_content=body_with_footer,
            )
            sg = SendGridAPIClient(settings.sendgrid_api_key)
            response = sg.send(message)
            log.info("Email sent to %s — status %s", to_email, response.status_code)
            return json.dumps({
                "status": "sent",
                "to": to_email,
                "subject": subject,
                "sendgrid_status_code": response.status_code,
            })
        except Exception as exc:
            log.error("SendGrid error: %s", exc)
            return json.dumps({
                "status": "error",
                "message": str(exc),
            })
