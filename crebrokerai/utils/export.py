"""CSV / report export utilities."""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

from sqlalchemy.orm import Session

from crebrokerai.config.models import Prospect, OutreachLog, Property
from crebrokerai.config.settings import settings


def _ensure_export_dir() -> Path:
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    return settings.export_dir


def export_prospects_csv(db: Session) -> Path:
    """Export all prospects to a timestamped CSV file."""
    out_dir = _ensure_export_dir()
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"prospects_{ts}.csv"
    prospects = db.query(Prospect).order_by(Prospect.lead_score.desc().nullslast()).all()
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "Company", "Industry", "Employees", "City", "State",
            "Lease SqFt", "Lease Expiry", "Funding Stage", "Recent Funding ($M)",
            "Growth Signal", "Decision Maker", "Title", "Email", "Phone",
            "Lead Score", "Tier",
        ])
        for p in prospects:
            writer.writerow([
                p.id, p.company_name, p.industry, p.employee_count,
                p.hq_city, p.hq_state, p.current_lease_sqft, p.lease_expiry,
                p.funding_stage, p.recent_funding_m, p.growth_signal,
                p.decision_maker_name, p.decision_maker_title,
                p.decision_maker_email, p.decision_maker_phone,
                p.lead_score, p.lead_tier,
            ])
    return path


def export_outreach_csv(db: Session) -> Path:
    """Export outreach log to CSV."""
    out_dir = _ensure_export_dir()
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"outreach_{ts}.csv"
    logs = db.query(OutreachLog).order_by(OutreachLog.sent_at.desc()).all()
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "Prospect ID", "Channel", "Status", "Subject", "Sent At", "Opt-Out",
        ])
        for log in logs:
            writer.writerow([
                log.id, log.prospect_id, log.channel, log.status,
                log.subject, log.sent_at, log.opt_out,
            ])
    return path
