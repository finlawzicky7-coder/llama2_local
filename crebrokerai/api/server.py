"""FastAPI application — optional microservice for webhooks and API access."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from crebrokerai.config.database import get_db, init_db
from crebrokerai.config.models import Prospect, Property, OutreachLog, CampaignRun
from crebrokerai.config.settings import settings
from crebrokerai.data.seed import seed_all
from crebrokerai.crews.campaign.crew import run_mock_campaign
from crebrokerai.utils.logging import get_logger

log = get_logger("api")

app = FastAPI(
    title="CREBrokerAI API",
    version="1.0.0",
    description="REST API for the CREBrokerAI tenant-prospecting platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ──────────────────────────────────────────────────────────────────


@app.on_event("startup")
def on_startup():
    seed_all()
    log.info("CREBrokerAI API started on port %d", settings.api_port)


# ── Pydantic schemas ────────────────────────────────────────────────────────


class CampaignRequest(BaseModel):
    name: str = "API Campaign"
    target_markets: list[str] = ["Austin", "Miami", "Denver"]
    target_industries: list[str] = ["Technology", "Biotech", "Financial Services"]


class ProspectOut(BaseModel):
    id: int
    company_name: str
    industry: str
    employee_count: int
    hq_city: str
    hq_state: str
    current_lease_sqft: Optional[int]
    lease_expiry: Optional[str]
    lead_score: Optional[float]
    lead_tier: str
    decision_maker_name: str
    decision_maker_email: str

    model_config = {"from_attributes": True}


class PropertyOut(BaseModel):
    id: int
    building_name: str
    address: str
    city: str
    state: str
    property_type: str
    available_sqft: int
    asking_rent_psf: float
    amenities: str
    is_available: bool

    model_config = {"from_attributes": True}


# ── Endpoints ────────────────────────────────────────────────────────────────


@app.get("/")
def root():
    return {"service": "CREBrokerAI API", "version": "1.0.0", "status": "running"}


@app.get("/prospects", response_model=list[ProspectOut])
def list_prospects(
    tier: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Prospect)
    if tier:
        q = q.filter(Prospect.lead_tier == tier)
    return q.order_by(Prospect.lead_score.desc().nullslast()).all()


@app.get("/prospects/{prospect_id}", response_model=ProspectOut)
def get_prospect(prospect_id: int, db: Session = Depends(get_db)):
    p = db.query(Prospect).get(prospect_id)
    if not p:
        raise HTTPException(404, "Prospect not found")
    return p


@app.get("/properties", response_model=list[PropertyOut])
def list_properties(
    city: Optional[str] = None,
    property_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Property).filter(Property.is_available.is_(True))
    if city:
        q = q.filter(Property.city.ilike(f"%{city}%"))
    if property_type:
        q = q.filter(Property.property_type == property_type)
    return q.all()


@app.get("/properties/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    p = db.query(Property).get(property_id)
    if not p:
        raise HTTPException(404, "Property not found")
    return p


@app.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(CampaignRun).order_by(CampaignRun.created_at.desc()).all()


@app.post("/campaigns/run")
def run_campaign(req: CampaignRequest):
    """Run a mock campaign (synchronous for demo — use async/Celery in production)."""
    result = run_mock_campaign(
        campaign_name=req.name,
        target_markets=req.target_markets,
        target_industries=req.target_industries,
    )
    return result


@app.get("/outreach")
def list_outreach(db: Session = Depends(get_db)):
    return db.query(OutreachLog).order_by(OutreachLog.sent_at.desc()).limit(100).all()


@app.get("/health")
def health():
    return {"status": "healthy"}
