"""Load mock JSON data into the database."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from crebrokerai.config.database import SessionLocal, init_db
from crebrokerai.config.models import Prospect, Property


DATA_DIR = Path(__file__).resolve().parent


def seed_prospects(db: Session) -> int:
    """Insert mock prospects if table is empty. Returns count inserted."""
    if db.query(Prospect).count() > 0:
        return 0
    raw = json.loads((DATA_DIR / "mock_prospects.json").read_text())
    count = 0
    for item in raw:
        db.add(Prospect(**item))
        count += 1
    db.commit()
    return count


def seed_properties(db: Session) -> int:
    """Insert mock properties if table is empty. Returns count inserted."""
    if db.query(Property).count() > 0:
        return 0
    raw = json.loads((DATA_DIR / "mock_properties.json").read_text())
    count = 0
    for item in raw:
        db.add(Property(**item))
        count += 1
    db.commit()
    return count


def seed_all() -> dict[str, int]:
    """Initialise database and seed all mock data."""
    init_db()
    db = SessionLocal()
    try:
        prospects = seed_prospects(db)
        properties = seed_properties(db)
        return {"prospects": prospects, "properties": properties}
    finally:
        db.close()


if __name__ == "__main__":
    result = seed_all()
    print(f"Seeded: {result}")
