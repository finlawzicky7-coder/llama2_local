"""Deterministic lead-scoring tool — complements the LLM-based scoring agent."""

from __future__ import annotations

import json
import datetime as dt

from crewai.tools import BaseTool

from crebrokerai.utils.logging import get_logger

log = get_logger("tools.scoring")


class LeadScoringTool(BaseTool):
    """Score a prospect 1-100 using a weighted formula."""

    name: str = "score_lead"
    description: str = (
        "Calculate a deterministic lead score for a prospect. "
        "Input: JSON with 'lease_expiry' (YYYY-MM-DD), 'growth_signal_strength' "
        "(high/medium/low), 'recent_funding_m' (float), 'market_heat' "
        "(hot/warm/cool), 'size_fit' (good/partial/poor). "
        "Returns score 1-100 and tier (hot/warm/cold)."
    )

    def _run(self, prospect_json: str) -> str:
        try:
            data = json.loads(prospect_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON"})

        score = 0
        breakdown = {}

        # ── Lease urgency (0-30) ─────────────────────────────
        lease_str = data.get("lease_expiry", "")
        if lease_str:
            try:
                expiry = dt.date.fromisoformat(lease_str)
                months_out = (expiry - dt.date.today()).days / 30
                if months_out <= 6:
                    pts = 30
                elif months_out <= 12:
                    pts = 20
                elif months_out <= 18:
                    pts = 10
                else:
                    pts = 3
            except ValueError:
                pts = 5
        else:
            pts = 5
        breakdown["lease_urgency"] = pts
        score += pts

        # ── Growth signals (0-25) ────────────────────────────
        signal = data.get("growth_signal_strength", "low").lower()
        pts = {"high": 25, "medium": 15, "low": 5}.get(signal, 5)
        breakdown["growth_signals"] = pts
        score += pts

        # ── Funding recency (0-15) ───────────────────────────
        funding = float(data.get("recent_funding_m", 0))
        if funding >= 50:
            pts = 15
        elif funding >= 10:
            pts = 10
        elif funding > 0:
            pts = 5
        else:
            pts = 0
        breakdown["funding"] = pts
        score += pts

        # ── Market heat (0-15) ───────────────────────────────
        heat = data.get("market_heat", "warm").lower()
        pts = {"hot": 15, "warm": 10, "cool": 5}.get(heat, 5)
        breakdown["market_heat"] = pts
        score += pts

        # ── Size fit (0-15) ──────────────────────────────────
        fit = data.get("size_fit", "partial").lower()
        pts = {"good": 15, "partial": 10, "poor": 5}.get(fit, 5)
        breakdown["size_fit"] = pts
        score += pts

        # ── Tier ─────────────────────────────────────────────
        score = min(score, 100)
        if score >= 75:
            tier = "hot"
        elif score >= 50:
            tier = "warm"
        else:
            tier = "cold"

        result = {
            "lead_score": score,
            "lead_tier": tier,
            "score_breakdown": breakdown,
        }
        log.info("Scored prospect: %d (%s)", score, tier)
        return json.dumps(result)
