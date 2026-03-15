"""CRE data tools — mock implementations with real-API placeholders.

In production, these would call Reonomy, CoStar, Attom Data, or Altus Group APIs.
The mock versions return realistic synthetic data so the package runs out-of-the-box.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from crewai.tools import BaseTool
from pydantic import Field

from crebrokerai.utils.logging import get_logger

log = get_logger("tools.cre_data")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class CRELeaseSearchTool(BaseTool):
    """Search for companies with expiring commercial leases in target markets."""

    name: str = "cre_lease_search"
    description: str = (
        "Search for companies with expiring commercial leases. "
        "Input: JSON with 'markets' (list of cities) and 'industries' (list). "
        "Returns mock lease expiration data. In production, calls Reonomy/CoStar API."
    )

    def _run(self, query: str) -> str:
        log.info("CRE Lease Search: %s", query)

        # Load mock prospects and filter by market/industry
        mock_path = DATA_DIR / "mock_prospects.json"
        prospects = json.loads(mock_path.read_text())

        try:
            params = json.loads(query)
            markets = [m.lower() for m in params.get("markets", [])]
            industries = [i.lower() for i in params.get("industries", [])]
        except (json.JSONDecodeError, AttributeError):
            markets, industries = [], []

        results = []
        for p in prospects:
            city_match = not markets or p["hq_city"].lower() in markets
            ind_match = not industries or any(
                ind in p["industry"].lower() for ind in industries
            )
            if city_match or ind_match:
                results.append({
                    "company_name": p["company_name"],
                    "industry": p["industry"],
                    "city": p["hq_city"],
                    "state": p["hq_state"],
                    "estimated_lease_sqft": p["current_lease_sqft"],
                    "lease_expiry_date": p["lease_expiry"],
                    "data_source": "mock_cre_database",
                })

        # If no filters matched, return all
        if not results:
            results = [
                {
                    "company_name": p["company_name"],
                    "industry": p["industry"],
                    "city": p["hq_city"],
                    "state": p["hq_state"],
                    "estimated_lease_sqft": p["current_lease_sqft"],
                    "lease_expiry_date": p["lease_expiry"],
                    "data_source": "mock_cre_database",
                }
                for p in prospects
            ]

        log.info("Found %d lease records", len(results))
        return json.dumps(results, indent=2)


class CRECompanyResearchTool(BaseTool):
    """Research a company's real estate footprint and decision-makers."""

    name: str = "cre_company_research"
    description: str = (
        "Research a specific company for CRE prospecting. "
        "Input: company name (string). "
        "Returns company profile with decision-maker contacts. "
        "In production, calls GrowthFactor/LinkedIn/ZoomInfo APIs."
    )

    def _run(self, company_name: str) -> str:
        log.info("Company Research: %s", company_name)

        mock_path = DATA_DIR / "mock_prospects.json"
        prospects = json.loads(mock_path.read_text())

        # Find matching company
        for p in prospects:
            if company_name.lower() in p["company_name"].lower():
                return json.dumps(p, indent=2)

        # If not found, generate a synthetic profile
        return json.dumps({
            "company_name": company_name,
            "industry": "Technology",
            "employee_count": random.randint(20, 500),
            "hq_city": "Austin",
            "hq_state": "TX",
            "current_lease_sqft": random.randint(2000, 50000),
            "lease_expiry": "2027-06-30",
            "funding_stage": random.choice(["Seed", "Series A", "Series B"]),
            "recent_funding_m": round(random.uniform(0, 100), 1),
            "growth_signal": "Hiring across multiple departments",
            "decision_maker_name": "Jane Doe",
            "decision_maker_title": "VP of Operations",
            "decision_maker_email": f"contact@{company_name.lower().replace(' ', '')}-demo.com",
            "decision_maker_phone": "+15125550000",
            "data_source": "synthetic",
        }, indent=2)
