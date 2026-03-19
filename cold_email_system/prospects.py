"""Prospect management — load, validate, and filter prospects from CSV."""

import csv
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Prospect:
    email: str
    first_name: str
    company: str
    industry: str
    pain_point: str
    title: str = ""
    website: str = ""
    notes: str = ""


REQUIRED_FIELDS = {"email", "first_name", "company", "industry", "pain_point"}


def load_prospects(csv_path: str) -> List[Prospect]:
    """Load prospects from a CSV file. Skips rows missing required fields."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Prospects file not found: {csv_path}")

    prospects: List[Prospect] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # row 1 is header
            missing = REQUIRED_FIELDS - set(row.keys())
            if missing:
                print(f"[WARN] Row {i}: missing columns {missing}, skipping")
                continue

            # Skip rows with empty required fields
            empty = [k for k in REQUIRED_FIELDS if not row.get(k, "").strip()]
            if empty:
                print(f"[WARN] Row {i}: empty required fields {empty}, skipping")
                continue

            prospects.append(
                Prospect(
                    email=row["email"].strip(),
                    first_name=row["first_name"].strip(),
                    company=row["company"].strip(),
                    industry=row["industry"].strip(),
                    pain_point=row["pain_point"].strip(),
                    title=row.get("title", "").strip(),
                    website=row.get("website", "").strip(),
                    notes=row.get("notes", "").strip(),
                )
            )
    return prospects


def filter_prospects(
    prospects: List[Prospect],
    industry: Optional[str] = None,
    exclude_emails: Optional[set] = None,
) -> List[Prospect]:
    """Filter prospects by industry and/or exclude already-contacted emails."""
    result = prospects
    if industry:
        result = [p for p in result if p.industry.lower() == industry.lower()]
    if exclude_emails:
        result = [p for p in result if p.email not in exclude_emails]
    return result
