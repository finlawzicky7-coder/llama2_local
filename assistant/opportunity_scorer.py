"""Score and rank opportunities based on relevance, effort, and potential value."""

import json
import os
from datetime import datetime

SCORES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "opportunity_scores.json")

SCORING_RULES = {
    "high_value_keywords": {
        "words": ["paid", "bounty", "contract", "revenue", "funding", "grant",
                  "sponsorship", "commission", "budget", "$"],
        "bonus": 30,
        "max_matches": 3,
    },
    "tech_match_keywords": {
        "words": ["python", "rust", "javascript", "typescript", "react",
                  "django", "fastapi", "api", "backend", "devops", "linux"],
        "bonus": 15,
        "max_matches": 4,
    },
    "opportunity_type_keywords": {
        "words": ["remote", "freelance", "part-time", "async", "flexible"],
        "bonus": 10,
        "max_matches": 3,
    },
    "urgency_keywords": {
        "words": ["asap", "urgent", "immediately", "this week", "deadline"],
        "bonus": 5,
        "max_matches": 2,
    },
}


def _load_scores():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"scored": [], "dismissed_urls": []}


def _save_scores(data):
    with open(SCORES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def score_opportunity(opportunity):
    """Score a single opportunity based on keyword matching and metadata."""
    score = 0
    reasons = []

    # Build searchable text from all string fields
    searchable = " ".join(str(v) for v in opportunity.values() if isinstance(v, str)).lower()
    for list_field in ("keywords", "labels", "topics"):
        if isinstance(opportunity.get(list_field), list):
            searchable += " " + " ".join(str(x) for x in opportunity[list_field])

    for rule_name, rule in SCORING_RULES.items():
        matches = [w for w in rule["words"] if w in searchable]
        if matches:
            # Cap the number of matches that contribute to score
            capped = min(len(matches), rule.get("max_matches", 3))
            score += rule["bonus"] * capped
            reasons.append(f"{rule_name}: {', '.join(matches[:3])}")

    # Bonus for GitHub stars
    stars = opportunity.get("stars", 0)
    if stars > 1000:
        score += 20
        reasons.append(f"popular ({stars} stars)")
    elif stars > 100:
        score += 10

    return {
        **opportunity,
        "score": score,
        "reasons": reasons,
        "scored_at": datetime.now().isoformat(),
    }


def rank_opportunities(opportunities):
    """Score and rank a list of opportunities."""
    scored = [score_opportunity(opp) for opp in opportunities]
    scored.sort(key=lambda x: x["score"], reverse=True)

    data = _load_scores()
    data["scored"].extend(scored)
    data["scored"] = data["scored"][-200:]
    _save_scores(data)

    return scored


def get_top_opportunities(limit=5):
    """Get the top-scored opportunities from history, excluding dismissed ones."""
    data = _load_scores()
    dismissed_urls = set(data.get("dismissed_urls", []))
    active = [s for s in data["scored"] if s.get("url") not in dismissed_urls]
    active.sort(key=lambda x: x.get("score", 0), reverse=True)
    return active[:limit]


def dismiss_opportunity(index):
    """Dismiss an opportunity by index (0-based from top list)."""
    data = _load_scores()
    dismissed_urls = set(data.get("dismissed_urls", []))
    active = [s for s in data["scored"] if s.get("url") not in dismissed_urls]
    active.sort(key=lambda x: x.get("score", 0), reverse=True)

    if 0 <= index < len(active):
        url = active[index].get("url", "")
        if url:
            data.setdefault("dismissed_urls", []).append(url)
            data["dismissed_urls"] = data["dismissed_urls"][-100:]
            _save_scores(data)
        return active[index]
    return None


def format_scored_report(scored, limit=5):
    """Format top scored opportunities for Telegram."""
    if not scored:
        return "No scored opportunities yet."

    top = sorted(scored, key=lambda x: x.get("score", 0), reverse=True)[:limit]

    msg = "*🏆 Top Opportunities*\n\n"
    for i, opp in enumerate(top):
        title = opp.get("title", opp.get("name", "Untitled"))[:100]
        source = opp.get("source", "Unknown")
        score = opp.get("score", 0)
        url = opp.get("url", "")
        reasons = ", ".join(opp.get("reasons", [])[:2])

        msg += f"*{i+1}. [{source}] {title}*\n"
        msg += f"   Score: *{score}* | {reasons}\n"
        if url:
            msg += f"   {url}\n"
        msg += "\n"

    return msg
