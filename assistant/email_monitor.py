"""Email monitor — polls IMAP inbox for opportunities and important messages."""

import imaplib
import email
import email.header
import os
import json
import re
import logging
from datetime import datetime, timedelta

log = logging.getLogger("email")

EMAIL_STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "email_state.json")

# Opportunity keywords to flag
OPPORTUNITY_KEYWORDS = [
    "freelance", "contract", "gig", "opportunity", "collaboration",
    "partnership", "proposal", "project", "budget", "rate",
    "hiring", "position", "role", "offer", "grant", "funding",
    "sponsorship", "bounty", "reward", "commission", "invoice",
    "payment", "revenue", "deal", "pitch",
]

# Pay extraction patterns for emails
PAY_PATTERNS = [
    re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*/\s*(?:hr|hour)", re.I),
    re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*[kK]"),
    re.compile(r"budget[:\s]*\$\s?([\d,]+)", re.I),
    re.compile(r"rate[:\s]*\$\s?([\d,]+)", re.I),
    re.compile(r"\$\s?([\d,]+(?:\.\d+)?)", re.I),
]


def _load_email_config():
    """Load email config from .env."""
    config = {}
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config


def _load_state():
    if os.path.exists(EMAIL_STATE_FILE):
        try:
            with open(EMAIL_STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_uid": "0", "flagged": [], "processed_count": 0}


def _save_state(state):
    with open(EMAIL_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _decode_header(header_value):
    """Decode email header handling various encodings."""
    if not header_value:
        return ""
    try:
        decoded_parts = email.header.decode_header(header_value)
        parts = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                parts.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                parts.append(part)
        return " ".join(parts)
    except Exception:
        return str(header_value)


def _extract_pay(text):
    """Try to extract pay/budget from email text."""
    for pattern in PAY_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                amount = float(match.group(1).replace(",", ""))
                if amount >= 50:  # Skip tiny amounts
                    return {"amount": amount, "raw": match.group(0)}
            except ValueError:
                continue
    return None


def check_inbox():
    """Connect to IMAP and check for new emails with opportunity keywords."""
    config = _load_email_config()
    imap_server = config.get("IMAP_SERVER", "")
    imap_user = config.get("IMAP_USER", "")
    imap_pass = config.get("IMAP_PASSWORD", "")

    if not all([imap_server, imap_user, imap_pass]):
        log.info("IMAP not configured. Set IMAP_SERVER, IMAP_USER, IMAP_PASSWORD in .env")
        return []

    state = _load_state()
    flagged = []
    mail = None

    try:
        # Connect with timeout
        imaplib.IMAP4_SSL.timeout = 15
        mail = imaplib.IMAP4_SSL(imap_server, timeout=15)
        mail.login(imap_user, imap_pass)
        mail.select("INBOX")

        # Search for unseen emails from last 3 days
        since_date = (datetime.now() - timedelta(days=3)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(UNSEEN SINCE {since_date})')

        if status != "OK" or not messages[0]:
            mail.logout()
            return []

        msg_ids = messages[0].split()
        log.info("Found %d unseen emails to scan", len(msg_ids))

        for msg_id in msg_ids[-20:]:  # Process last 20 unseen
            try:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                msg = email.message_from_bytes(msg_data[0][1])
                subject = _decode_header(msg.get("Subject", ""))
                sender = _decode_header(msg.get("From", ""))
                date = msg.get("Date", "")

                # Get body text
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode("utf-8", errors="replace")[:2000]
                            break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode("utf-8", errors="replace")[:2000]

                # Check for opportunity keywords
                searchable = (subject + " " + body).lower()
                matches = [kw for kw in OPPORTUNITY_KEYWORDS if kw in searchable]

                if matches:
                    entry = {
                        "subject": subject[:150],
                        "from": sender[:100],
                        "date": date,
                        "keywords": matches[:5],
                        "snippet": body[:200].strip(),
                        "found": datetime.now().isoformat(),
                    }

                    # Extract pay info
                    pay = _extract_pay(searchable)
                    if pay:
                        entry["pay"] = pay

                    flagged.append(entry)

            except Exception as e:
                log.warning("Failed to process email %s: %s", msg_id, e)
                continue

        state["processed_count"] += len(msg_ids)
        state["flagged"].extend(flagged)
        state["flagged"] = state["flagged"][-100:]
        _save_state(state)

    except imaplib.IMAP4.error as e:
        log.error("IMAP error: %s", e)
    except TimeoutError:
        log.error("IMAP connection timed out for %s", imap_server)
    except Exception as e:
        log.error("Email check failed: %s", e)
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass

    return flagged


def format_email_alerts(flagged):
    """Format flagged emails into a Telegram message."""
    if not flagged:
        return None

    msg = f"*📧 {len(flagged)} Opportunity Emails Found*\n\n"
    for e in flagged[:5]:
        kw = ", ".join(e["keywords"][:3])
        pay_str = ""
        if e.get("pay"):
            pay_str = f" 💵 {e['pay']['raw']}"
        msg += f"*From:* {e['from']}\n"
        msg += f"*Subject:* {e['subject']}{pay_str}\n"
        msg += f"*Keywords:* _{kw}_\n\n"

    if len(flagged) > 5:
        msg += f"_...and {len(flagged) - 5} more_"

    return msg
