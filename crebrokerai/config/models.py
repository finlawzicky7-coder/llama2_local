"""SQLAlchemy ORM models for CREBrokerAI."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, Boolean, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from crebrokerai.config.database import Base


class Prospect(Base):
    """A company that is a potential tenant prospect."""

    __tablename__ = "prospects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    industry: Mapped[str] = mapped_column(String(128), default="")
    employee_count: Mapped[int] = mapped_column(Integer, default=0)
    hq_city: Mapped[str] = mapped_column(String(128), default="")
    hq_state: Mapped[str] = mapped_column(String(64), default="")
    current_lease_sqft: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lease_expiry: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    funding_stage: Mapped[str] = mapped_column(String(64), default="")
    recent_funding_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    growth_signal: Mapped[str] = mapped_column(String(255), default="")
    decision_maker_name: Mapped[str] = mapped_column(String(255), default="")
    decision_maker_title: Mapped[str] = mapped_column(String(255), default="")
    decision_maker_email: Mapped[str] = mapped_column(String(255), default="")
    decision_maker_phone: Mapped[str] = mapped_column(String(64), default="")
    lead_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lead_tier: Mapped[str] = mapped_column(String(16), default="")  # hot / warm / cold
    notes: Mapped[str] = mapped_column(Text, default="")
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Property(Base):
    """An available commercial property / building."""

    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    building_name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(512))
    city: Mapped[str] = mapped_column(String(128))
    state: Mapped[str] = mapped_column(String(64))
    zip_code: Mapped[str] = mapped_column(String(16), default="")
    property_type: Mapped[str] = mapped_column(String(64))  # office / industrial / retail
    total_sqft: Mapped[int] = mapped_column(Integer, default=0)
    available_sqft: Mapped[int] = mapped_column(Integer, default=0)
    asking_rent_psf: Mapped[float] = mapped_column(Float, default=0.0)
    year_built: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    amenities: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(512), default="")
    broker_name: Mapped[str] = mapped_column(String(255), default="")
    broker_email: Mapped[str] = mapped_column(String(255), default="")
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())


class OutreachLog(Base):
    """Log of every outreach attempt (email or call)."""

    __tablename__ = "outreach_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prospect_id: Mapped[int] = mapped_column(Integer, index=True)
    channel: Mapped[str] = mapped_column(String(32))  # email / call
    status: Mapped[str] = mapped_column(String(32))  # sent / delivered / opened / replied / failed
    subject: Mapped[str] = mapped_column(String(512), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    response: Mapped[str] = mapped_column(Text, default="")
    sent_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())
    opt_out: Mapped[bool] = mapped_column(Boolean, default=False)


class CampaignRun(Base):
    """Top-level record for a full campaign execution."""

    __tablename__ = "campaign_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending/running/done/failed
    target_industries: Mapped[str] = mapped_column(Text, default="")
    target_markets: Mapped[str] = mapped_column(Text, default="")
    total_prospects: Mapped[int] = mapped_column(Integer, default=0)
    emails_sent: Mapped[int] = mapped_column(Integer, default=0)
    calls_made: Mapped[int] = mapped_column(Integer, default=0)
    tours_booked: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())
