"""Invoice tracker and payment clawback system.

Track invoices, detect overdue payments, generate follow-up reminders,
and calculate outstanding balances.
"""

import json
import os
import logging
import tempfile
from datetime import datetime, timedelta

log = logging.getLogger("invoices")

INVOICE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "invoices.json")

# Default follow-up schedule (days after due date)
FOLLOWUP_SCHEDULE = [0, 3, 7, 14, 30]

# Invoice statuses
STATUS_PENDING = "pending"       # Sent, not yet due
STATUS_OVERDUE = "overdue"       # Past due date
STATUS_PAID = "paid"             # Payment received
STATUS_PARTIAL = "partial"       # Partially paid
STATUS_DISPUTED = "disputed"     # Client disputes
STATUS_WRITTEN_OFF = "written_off"  # Given up


def _load_invoices():
    if os.path.exists(INVOICE_FILE):
        try:
            with open(INVOICE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"invoices": [], "next_id": 1, "followup_log": []}


def _save_invoices(data):
    try:
        dir_name = os.path.dirname(INVOICE_FILE)
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, INVOICE_FILE)
    except OSError as e:
        log.error("Failed to save invoices: %s", e)


def _next_id(data):
    nid = data.get("next_id", 1)
    data["next_id"] = nid + 1
    return nid


def create_invoice(client, amount, description="", due_days=30, net_terms=None):
    """Create a new invoice.

    Args:
        client: Client name or company
        amount: Dollar amount owed
        description: Work description
        due_days: Days until due (default 30)
        net_terms: Payment terms label (e.g., "NET30")
    """
    data = _load_invoices()
    now = datetime.now()

    invoice = {
        "id": _next_id(data),
        "client": client,
        "amount": float(amount),
        "paid_amount": 0.0,
        "description": description,
        "status": STATUS_PENDING,
        "created": now.isoformat(),
        "due_date": (now + timedelta(days=due_days)).strftime("%Y-%m-%d"),
        "net_terms": net_terms or f"NET{due_days}",
        "payments": [],
        "followups_sent": 0,
        "last_followup": None,
        "notes": "",
    }

    data["invoices"].append(invoice)
    _save_invoices(data)
    log.info("Invoice #%d created: $%.2f for %s", invoice["id"], amount, client)
    return invoice


def record_payment(invoice_id, amount, note=""):
    """Record a payment against an invoice."""
    data = _load_invoices()

    for inv in data["invoices"]:
        if inv["id"] == invoice_id:
            payment = {
                "amount": float(amount),
                "date": datetime.now().isoformat(),
                "note": note,
            }
            inv["payments"].append(payment)
            inv["paid_amount"] = sum(p["amount"] for p in inv["payments"])

            if inv["paid_amount"] >= inv["amount"]:
                inv["status"] = STATUS_PAID
            elif inv["paid_amount"] > 0:
                inv["status"] = STATUS_PARTIAL

            _save_invoices(data)
            log.info("Payment $%.2f recorded for invoice #%d", amount, invoice_id)
            return inv

    return None


def mark_disputed(invoice_id, reason=""):
    """Mark an invoice as disputed."""
    data = _load_invoices()
    for inv in data["invoices"]:
        if inv["id"] == invoice_id:
            inv["status"] = STATUS_DISPUTED
            inv["notes"] = reason or inv.get("notes", "")
            _save_invoices(data)
            return inv
    return None


def write_off(invoice_id):
    """Write off an invoice as uncollectable."""
    data = _load_invoices()
    for inv in data["invoices"]:
        if inv["id"] == invoice_id:
            inv["status"] = STATUS_WRITTEN_OFF
            _save_invoices(data)
            return inv
    return None


def get_invoice(invoice_id):
    """Get a specific invoice by ID."""
    data = _load_invoices()
    for inv in data["invoices"]:
        if inv["id"] == invoice_id:
            return inv
    return None


def list_invoices(status=None):
    """List invoices, optionally filtered by status."""
    data = _load_invoices()
    invoices = data["invoices"]
    if status:
        invoices = [i for i in invoices if i["status"] == status]
    return invoices


def check_overdue():
    """Check for overdue invoices and update their status.

    Returns list of newly overdue invoices (for alerting).
    """
    data = _load_invoices()
    today = datetime.now().strftime("%Y-%m-%d")
    newly_overdue = []

    for inv in data["invoices"]:
        if inv["status"] == STATUS_PENDING and inv["due_date"] < today:
            inv["status"] = STATUS_OVERDUE
            newly_overdue.append(inv)

    if newly_overdue:
        _save_invoices(data)
        log.info("%d invoices became overdue", len(newly_overdue))

    return newly_overdue


def get_followup_needed():
    """Get invoices that need follow-up based on schedule.

    Returns invoices where enough time has passed since last follow-up.
    """
    data = _load_invoices()
    now = datetime.now()
    needs_followup = []

    for inv in data["invoices"]:
        if inv["status"] not in (STATUS_OVERDUE, STATUS_PARTIAL):
            continue

        # How many days overdue?
        try:
            due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
            days_overdue = (now - due).days
        except ValueError:
            continue

        if days_overdue < 0:
            continue

        # Determine next follow-up threshold
        followups_sent = inv.get("followups_sent", 0)
        if followups_sent >= len(FOLLOWUP_SCHEDULE):
            continue  # All follow-ups exhausted

        next_threshold = FOLLOWUP_SCHEDULE[followups_sent]
        if days_overdue >= next_threshold:
            # Check cooldown — at least 2 days between follow-ups
            last = inv.get("last_followup")
            if last:
                try:
                    last_date = datetime.fromisoformat(last)
                    if (now - last_date).days < 2:
                        continue
                except ValueError:
                    pass

            needs_followup.append({
                **inv,
                "days_overdue": days_overdue,
                "followup_number": followups_sent + 1,
            })

    return needs_followup


def record_followup(invoice_id):
    """Record that a follow-up was sent for an invoice."""
    data = _load_invoices()
    for inv in data["invoices"]:
        if inv["id"] == invoice_id:
            inv["followups_sent"] = inv.get("followups_sent", 0) + 1
            inv["last_followup"] = datetime.now().isoformat()
            data["followup_log"].append({
                "invoice_id": invoice_id,
                "date": datetime.now().isoformat(),
                "number": inv["followups_sent"],
            })
            _save_invoices(data)
            return inv
    return None


def get_outstanding_summary():
    """Get summary of all outstanding money owed."""
    data = _load_invoices()
    summary = {
        "total_outstanding": 0,
        "total_overdue": 0,
        "total_partial": 0,
        "total_collected": 0,
        "total_written_off": 0,
        "by_client": {},
        "overdue_count": 0,
        "pending_count": 0,
    }

    for inv in data["invoices"]:
        owed = inv["amount"] - inv.get("paid_amount", 0)
        client = inv["client"]

        if inv["status"] == STATUS_PAID:
            summary["total_collected"] += inv["amount"]
        elif inv["status"] == STATUS_WRITTEN_OFF:
            summary["total_written_off"] += owed
        elif inv["status"] == STATUS_OVERDUE:
            summary["total_overdue"] += owed
            summary["total_outstanding"] += owed
            summary["overdue_count"] += 1
        elif inv["status"] == STATUS_PARTIAL:
            summary["total_partial"] += owed
            summary["total_outstanding"] += owed
        elif inv["status"] == STATUS_PENDING:
            summary["total_outstanding"] += owed
            summary["pending_count"] += 1

        # Per-client breakdown
        if inv["status"] not in (STATUS_PAID, STATUS_WRITTEN_OFF):
            if client not in summary["by_client"]:
                summary["by_client"][client] = {"owed": 0, "invoices": 0}
            summary["by_client"][client]["owed"] += owed
            summary["by_client"][client]["invoices"] += 1

    return summary


def generate_followup_message(invoice):
    """Generate a professional follow-up message template for an overdue invoice."""
    days = invoice.get("days_overdue", 0)
    followup_num = invoice.get("followup_number", 1)
    amount_owed = invoice["amount"] - invoice.get("paid_amount", 0)

    if followup_num == 1:
        tone = "friendly"
        subject = f"Friendly reminder: Invoice #{invoice['id']} is due"
        body = (
            f"Hi,\n\n"
            f"Just a quick reminder that invoice #{invoice['id']} for "
            f"${amount_owed:,.2f} ({invoice.get('description', 'services rendered')}) "
            f"was due on {invoice['due_date']}.\n\n"
            f"Please let me know if you have any questions or if payment is on its way.\n\n"
            f"Thanks!"
        )
    elif followup_num == 2:
        tone = "firm"
        subject = f"Follow-up: Invoice #{invoice['id']} — {days} days overdue"
        body = (
            f"Hi,\n\n"
            f"I'm following up on invoice #{invoice['id']} for ${amount_owed:,.2f}, "
            f"which is now {days} days past due (originally due {invoice['due_date']}).\n\n"
            f"Could you provide an update on when I can expect payment?\n\n"
            f"Best regards"
        )
    elif followup_num == 3:
        tone = "serious"
        subject = f"Urgent: Invoice #{invoice['id']} — {days} days overdue"
        body = (
            f"Hi,\n\n"
            f"This is my third follow-up regarding invoice #{invoice['id']} for "
            f"${amount_owed:,.2f}, now {days} days overdue.\n\n"
            f"I need to receive payment or a payment plan by "
            f"{(datetime.now() + timedelta(days=7)).strftime('%B %d')}.\n\n"
            f"Please respond at your earliest convenience."
        )
    else:
        tone = "final"
        subject = f"Final notice: Invoice #{invoice['id']} — ${amount_owed:,.2f} outstanding"
        body = (
            f"Hi,\n\n"
            f"This is a final notice regarding invoice #{invoice['id']} for "
            f"${amount_owed:,.2f}, which has been outstanding for {days} days.\n\n"
            f"If I don't receive payment or a response within 7 days, "
            f"I will need to consider alternative collection measures.\n\n"
            f"Please contact me to resolve this."
        )

    return {
        "subject": subject,
        "body": body,
        "tone": tone,
        "followup_number": followup_num,
    }


# === Telegram formatting ===

def format_invoices_list(invoices, title="Invoices"):
    """Format invoice list for Telegram."""
    if not invoices:
        return "No invoices found."

    msg = f"*{title}*\n\n"
    for inv in invoices:
        owed = inv["amount"] - inv.get("paid_amount", 0)
        status_icon = {
            STATUS_PENDING: "🔵",
            STATUS_OVERDUE: "🔴",
            STATUS_PAID: "✅",
            STATUS_PARTIAL: "🟡",
            STATUS_DISPUTED: "⚠️",
            STATUS_WRITTEN_OFF: "❌",
        }.get(inv["status"], "❓")

        msg += f"{status_icon} *#{inv['id']}* {inv['client']} — "
        if inv["status"] == STATUS_PAID:
            msg += f"${inv['amount']:,.2f} ✅ Paid\n"
        else:
            msg += f"*${owed:,.2f}* owed"
            if inv["status"] == STATUS_OVERDUE:
                try:
                    due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
                    days = (datetime.now() - due).days
                    msg += f" ({days}d overdue)"
                except ValueError:
                    pass
            msg += f"\n"

        if inv.get("description"):
            msg += f"  _{inv['description'][:60]}_\n"
        msg += f"  Due: {inv['due_date']} | {inv.get('net_terms', '')}\n\n"

    return msg


def format_overdue_alert(overdue_invoices):
    """Format overdue alert for Telegram."""
    if not overdue_invoices:
        return None

    total = sum(i["amount"] - i.get("paid_amount", 0) for i in overdue_invoices)
    msg = f"*🔴 {len(overdue_invoices)} Overdue Invoice(s) — ${total:,.2f} outstanding*\n\n"

    for inv in overdue_invoices:
        owed = inv["amount"] - inv.get("paid_amount", 0)
        try:
            due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
            days = (datetime.now() - due).days
        except ValueError:
            days = 0
        msg += f"  🔴 *#{inv['id']}* {inv['client']}: *${owed:,.2f}* ({days}d overdue)\n"

    msg += "\nUse /nudge <id> to generate a follow-up message."
    return msg


def format_followup_alert(followup_list):
    """Format follow-up needed alert for Telegram."""
    if not followup_list:
        return None

    msg = "*📬 Follow-ups Needed*\n\n"
    for inv in followup_list:
        owed = inv["amount"] - inv.get("paid_amount", 0)
        msg += (
            f"*#{inv['id']}* {inv['client']}: *${owed:,.2f}* "
            f"({inv['days_overdue']}d overdue, follow-up #{inv['followup_number']})\n"
        )
    msg += "\nUse /nudge <id> to generate follow-up text."
    return msg


def format_outstanding_summary(summary):
    """Format outstanding money summary for Telegram."""
    msg = "*💸 Outstanding Balance*\n\n"
    msg += f"Total outstanding: *${summary['total_outstanding']:,.2f}*\n"
    msg += f"  🔴 Overdue: ${summary['total_overdue']:,.2f} ({summary['overdue_count']} invoices)\n"
    msg += f"  🔵 Pending: ${summary['total_outstanding'] - summary['total_overdue']:,.2f} ({summary['pending_count']})\n"
    msg += f"  🟡 Partial: ${summary['total_partial']:,.2f}\n"
    msg += f"\nCollected all-time: *${summary['total_collected']:,.2f}*\n"

    if summary["total_written_off"] > 0:
        msg += f"Written off: ${summary['total_written_off']:,.2f}\n"

    if summary["by_client"]:
        msg += "\n*By Client:*\n"
        sorted_clients = sorted(
            summary["by_client"].items(),
            key=lambda x: x[1]["owed"], reverse=True
        )
        for client, info in sorted_clients[:10]:
            msg += f"  {client}: *${info['owed']:,.2f}* ({info['invoices']} inv)\n"

    return msg
