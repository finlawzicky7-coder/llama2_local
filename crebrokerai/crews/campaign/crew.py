"""Full Campaign Orchestration Crew.

The Campaign Manager coordinates all sub-crews into a single end-to-end
tenant-prospecting and leasing workflow. Includes human-in-the-loop
approval before any real outbound communications.
"""

from __future__ import annotations

import json
import datetime as dt
from pathlib import Path

from crewai import Agent, Crew, Process, Task

from crebrokerai.config.database import SessionLocal, init_db
from crebrokerai.config.models import CampaignRun, Prospect
from crebrokerai.crews.prospecting.crew import ProspectingCrew
from crebrokerai.crews.scoring.crew import ScoringCrew
from crebrokerai.crews.matching.crew import MatchingCrew
from crebrokerai.crews.outreach.crew import OutreachCrew
from crebrokerai.data.seed import seed_all
from crebrokerai.utils.logging import get_logger

log = get_logger("crews.campaign")

YAML_DIR = Path(__file__).resolve().parent


def _load_yaml(name: str) -> dict:
    import yaml

    return yaml.safe_load((YAML_DIR / name).read_text())


class CampaignCrew:
    """Top-level orchestrator that runs all sub-crews in sequence."""

    def __init__(
        self,
        campaign_name: str = "Default Campaign",
        target_markets: list[str] | None = None,
        target_industries: list[str] | None = None,
        human_approval: bool = True,
    ):
        self.campaign_name = campaign_name
        self.target_markets = target_markets or ["Austin", "Miami", "Denver"]
        self.target_industries = target_industries or ["Technology", "Biotech", "Financial Services"]
        self.human_approval = human_approval
        self.agents_cfg = _load_yaml("agents.yaml")
        self.tasks_cfg = _load_yaml("tasks.yaml")

    def run(self, progress_callback=None) -> dict:
        """Execute the full campaign pipeline.

        Args:
            progress_callback: Optional callable(stage: str, pct: int, msg: str)
                for Streamlit progress updates.

        Returns:
            Campaign summary dict.
        """
        def _progress(stage: str, pct: int, msg: str):
            log.info("[%s] %d%% — %s", stage, pct, msg)
            if progress_callback:
                progress_callback(stage, pct, msg)

        # ── Initialise ───────────────────────────────────────
        _progress("init", 0, "Initialising database and seeding mock data...")
        seed_all()

        db = SessionLocal()
        campaign = CampaignRun(
            name=self.campaign_name,
            status="running",
            target_industries=", ".join(self.target_industries),
            target_markets=", ".join(self.target_markets),
            started_at=dt.datetime.utcnow(),
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        results = {"campaign_id": campaign.id, "stages": {}}

        try:
            # ── Stage 1: Prospecting ─────────────────────────
            _progress("prospecting", 10, "Running Prospecting Crew...")
            prospecting = ProspectingCrew(self.target_markets, self.target_industries)
            prospect_result = prospecting.run()
            results["stages"]["prospecting"] = prospect_result
            _progress("prospecting", 25, "Prospecting complete")

            # ── Stage 2: Scoring ─────────────────────────────
            _progress("scoring", 30, "Running Scoring Crew...")
            scoring = ScoringCrew(prospect_result, self.target_markets)
            scoring_result = scoring.run()
            results["stages"]["scoring"] = scoring_result
            _progress("scoring", 50, "Scoring complete")

            # ── Stage 3: Matching ────────────────────────────
            _progress("matching", 55, "Running Matching Crew...")
            matching = MatchingCrew(prospect_result)
            matching_result = matching.run()
            results["stages"]["matching"] = matching_result
            _progress("matching", 70, "Matching complete")

            # ── Stage 4: Outreach ────────────────────────────
            _progress("outreach", 75, "Running Outreach Crew...")
            outreach = OutreachCrew(prospect_result)
            outreach_result = outreach.run()
            results["stages"]["outreach"] = outreach_result
            _progress("outreach", 90, "Outreach drafts ready")

            # ── Human Approval Gate ──────────────────────────
            if self.human_approval:
                results["human_approval_required"] = True
                results["status"] = "awaiting_approval"
                _progress("approval", 95, "AWAITING HUMAN APPROVAL before sending")
            else:
                results["status"] = "completed"

            # ── Update campaign record ───────────────────────
            prospect_count = db.query(Prospect).count()
            campaign.total_prospects = prospect_count
            campaign.status = results["status"]
            campaign.completed_at = dt.datetime.utcnow()
            db.commit()

            _progress("done", 100, "Campaign pipeline complete!")
            results["campaign_id"] = campaign.id
            results["total_prospects"] = prospect_count

        except Exception as exc:
            log.error("Campaign failed: %s", exc, exc_info=True)
            campaign.status = "failed"
            db.commit()
            results["status"] = "failed"
            results["error"] = str(exc)
        finally:
            db.close()

        return results


def run_mock_campaign(
    campaign_name: str = "Demo Campaign",
    target_markets: list[str] | None = None,
    target_industries: list[str] | None = None,
) -> dict:
    """Quick-start function to run a mock campaign without LLM keys.

    This uses the mock data directly, bypassing the LLM-powered agents,
    so the package runs fully out-of-the-box.
    """
    from crebrokerai.data.seed import seed_all
    from crebrokerai.config.database import SessionLocal
    from crebrokerai.config.models import Prospect, Property
    from crebrokerai.tools.scoring_tool import LeadScoringTool
    from crebrokerai.tools.matching_tool import PropertyMatchingTool

    log.info("Running MOCK campaign (no LLM keys required)")

    seed_all()
    db = SessionLocal()

    try:
        prospects = db.query(Prospect).all()
        properties = db.query(Property).all()

        scorer = LeadScoringTool()
        matcher = PropertyMatchingTool()

        scored_prospects = []
        for p in prospects:
            score_input = json.dumps({
                "lease_expiry": p.lease_expiry or "",
                "growth_signal_strength": "high" if "hiring" in (p.growth_signal or "").lower()
                    or "expand" in (p.growth_signal or "").lower() else "medium",
                "recent_funding_m": p.recent_funding_m or 0,
                "market_heat": "hot",
                "size_fit": "good",
            })
            score_result = json.loads(scorer._run(score_input))
            p.lead_score = score_result["lead_score"]
            p.lead_tier = score_result["lead_tier"]
            scored_prospects.append({
                "company_name": p.company_name,
                "lead_score": p.lead_score,
                "lead_tier": p.lead_tier,
                "score_breakdown": score_result["score_breakdown"],
            })

        db.commit()

        # Match top prospects to properties
        matches = []
        for p in prospects:
            if p.lead_tier in ("hot", "warm"):
                match_input = json.dumps({
                    "company_name": p.company_name,
                    "industry": p.industry,
                    "city": p.hq_city,
                    "state": p.hq_state,
                    "current_lease_sqft": p.current_lease_sqft or 5000,
                    "employee_count": p.employee_count,
                })
                match_result = json.loads(matcher._run(match_input))
                matches.append({
                    "prospect": p.company_name,
                    "tier": p.lead_tier,
                    "top_match": match_result[0]["building_name"] if match_result else "None",
                    "match_score": match_result[0]["match_score_pct"] if match_result else 0,
                })

        return {
            "status": "mock_completed",
            "campaign_name": campaign_name,
            "total_prospects": len(prospects),
            "scored_prospects": scored_prospects,
            "hot_leads": sum(1 for p in prospects if p.lead_tier == "hot"),
            "warm_leads": sum(1 for p in prospects if p.lead_tier == "warm"),
            "cold_leads": sum(1 for p in prospects if p.lead_tier == "cold"),
            "property_matches": matches,
            "total_properties": len(properties),
            "message": "Mock campaign complete! Add API keys to .env for full LLM-powered campaign.",
        }
    finally:
        db.close()
