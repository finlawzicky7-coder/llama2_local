"""Property-matching tool — algorithmic match between prospects and properties."""

from __future__ import annotations

import json
from pathlib import Path

from crewai.tools import BaseTool

from crebrokerai.utils.logging import get_logger

log = get_logger("tools.matching")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Industry → preferred property type mapping
INDUSTRY_TYPE_MAP = {
    "saas": "office",
    "technology": "office",
    "biotech": "office",        # lab-ready office
    "life sciences": "office",
    "logistics": "industrial",
    "supply chain": "industrial",
    "manufacturing": "industrial",
    "robotics": "industrial",
    "financial": "office",
    "healthcare": "office",
    "medtech": "office",
    "creative": "office",
    "advertising": "office",
    "legal": "office",
    "cleantech": "office",
    "energy": "office",
    "data analytics": "office",
    "ai": "office",
}


class PropertyMatchingTool(BaseTool):
    """Match a prospect to the best available properties."""

    name: str = "match_properties"
    description: str = (
        "Find the best property matches for a prospect. "
        "Input: JSON with 'company_name', 'industry', 'city', 'state', "
        "'current_lease_sqft', 'employee_count'. "
        "Returns top 3 matching properties ranked by fit score."
    )

    def _run(self, prospect_json: str) -> str:
        try:
            prospect = json.loads(prospect_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON"})

        properties = json.loads((DATA_DIR / "mock_properties.json").read_text())

        # Determine ideal space need (current + 30% growth buffer)
        current_sqft = prospect.get("current_lease_sqft", 5000)
        ideal_sqft = int(current_sqft * 1.3)
        industry = prospect.get("industry", "").lower()
        target_city = prospect.get("city", "").lower()
        target_state = prospect.get("state", "").lower()

        # Determine preferred property type from industry
        preferred_type = "office"
        for key, ptype in INDUSTRY_TYPE_MAP.items():
            if key in industry:
                preferred_type = ptype
                break

        scored = []
        for prop in properties:
            score = 0
            reasons = []

            # Location match (0-30)
            if prop["city"].lower() == target_city:
                score += 30
                reasons.append(f"Same city: {prop['city']}")
            elif prop["state"].lower() == target_state:
                score += 15
                reasons.append(f"Same state: {prop['state']}")

            # Size match (0-30)
            avail = prop["available_sqft"]
            if avail >= ideal_sqft * 0.8 and avail <= ideal_sqft * 2.0:
                score += 30
                reasons.append(f"Size fit: {avail:,} sqft available vs {ideal_sqft:,} needed")
            elif avail >= ideal_sqft * 0.5:
                score += 15
                reasons.append(f"Partial size fit: {avail:,} sqft")

            # Type match (0-20)
            if prop["property_type"] == preferred_type:
                score += 20
                reasons.append(f"Property type match: {preferred_type}")

            # Amenity relevance (0-10)
            amenities_lower = prop.get("amenities", "").lower()
            if "biotech" in industry or "life" in industry:
                if "lab" in amenities_lower:
                    score += 10
                    reasons.append("Lab-ready space")
            elif "creative" in industry or "advertising" in industry:
                if "ceiling" in amenities_lower or "loft" in amenities_lower or "gallery" in amenities_lower:
                    score += 10
                    reasons.append("Creative-friendly space")
            elif "logistics" in industry or "robotics" in industry:
                if "dock" in amenities_lower or "high-bay" in amenities_lower:
                    score += 10
                    reasons.append("Industrial-grade features")
            else:
                score += 5

            # Price competitiveness (0-10)
            if prop["asking_rent_psf"] < 50:
                score += 10
                reasons.append("Competitive rent")
            elif prop["asking_rent_psf"] < 70:
                score += 5

            # Estimated deal value
            deal_value = avail * prop["asking_rent_psf"]

            scored.append({
                "property_id": properties.index(prop) + 1,
                "building_name": prop["building_name"],
                "city": prop["city"],
                "state": prop["state"],
                "available_sqft": avail,
                "asking_rent_psf": prop["asking_rent_psf"],
                "match_score_pct": min(score, 100),
                "match_reasons": reasons,
                "potential_deal_value": round(deal_value, 2),
            })

        # Sort by score descending, return top 3
        scored.sort(key=lambda x: x["match_score_pct"], reverse=True)
        top_matches = scored[:3]

        log.info("Matched %s to %d properties", prospect.get("company_name", "?"), len(top_matches))
        return json.dumps(top_matches, indent=2)
