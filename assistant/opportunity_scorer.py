"""Score and rank opportunities based on pay, relevance, and freshness."""

import json
import os
import logging
from datetime import datetime, timedelta

log = logging.getLogger("scorer")

SCORES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "opportunity_scores.json")
USER_MD = os.path.join(os.path.dirname(os.path.dirname(__file__)), "USER.md")

# Keywords that indicate real paid work
PAID_KEYWORDS = ["paid", "bounty", "contract", "revenue", "funding", "grant",
                 "sponsorship", "commission", "budget", "salary", "compensation"]

# User skills — loaded from USER.md, fallback to defaults
DEFAULT_SKILLS = ["python", "rust", "javascript", "typescript", "react",
                  "django", "fastapi", "api", "backend", "devops", "linux",
                  "aws", "docker", "kubernetes"]

WORK_TYPE_KEYWORDS = ["remote", "freelance", "part-time", "async", "flexible", "contractor"]
URGENCY_KEYWORDS = ["asap", "urgent", "immediately", "this week", "deadline", "hiring now"]

# Penalty keywords — these aren't worth pursuing
PENALTY_KEYWORDS = ["unpaid", "volunteer", "exposure", "equity only", "for experience"]


def _load_user_skills():
    """Load user skills from USER.md."""
    try:
        if os.path.exists(USER_MD):
            with open(USER_MD) as f:
                content = f.read().lower()
            # Look for skills section
            if "## skills" in content:
                import re
                skills_section = re.search(r"## skills\s*\n(.*?)(?:\n## |\Z)", content, re.DOTALL)
                if skills_section:
                    # Extract words that look like skills
                    words = re.findall(r"[a-z][a-z0-9+#.-]+", skills_section.group(1))
                    if words:
                        return words
    except OSError:
        pass
    return DEFAULT_SKILLS


def _load_scores():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"scored": [], "dismissed_urls": [], "earnings_log": []}


def _save_scores(data):
    with open(SCORES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def score_opportunity(opportunity, user_skills=None):
    """Score a single opportunity. Higher score = more profitable/relevant."""
    score = 0
    reasons = []
    skills = user_skills or DEFAULT_SKILLS

    # Build searchable text
    searchable = " ".join(str(v) for v in opportunity.values() if isinstance(v, str)).lower()
    for list_field in ("keywords", "labels", "topics"):
        if isinstance(opportunity.get(list_field), list):
            searchable += " " + " ".join(str(x).lower() for x in opportunity[list_field])

    # === MONEY SCORE (biggest weight) ===
    pay = opportunity.get("pay")
    if pay:
        amount = pay.get("amount", 0)
        hourly = pay.get("hourly_equiv")

        if hourly and hourly > 0:
            # Score based on hourly rate — $100/hr = 100 points
            score += min(int(hourly), 200)
            reasons.append(f"💵 ~${hourly:.0f}/hr")
        elif amount > 0:
            # Fixed amounts: $1000 = 50 points, $5000 = 100, $10000 = 150
            score += min(int(amount / 20), 200)
            reasons.append(f"💵 ${amount:,.0f}")
    else:
        # Check for pay keywords without extracted amount
        pay_matches = [kw for kw in PAID_KEYWORDS if kw in searchable]
        if pay_matches:
            score += 20
            reasons.append(f"pay indicators: {', '.join(pay_matches[:2])}")

    # === SKILL MATCH ===
    skill_matches = [s for s in skills if s in searchable]
    if skill_matches:
        score += min(len(skill_matches) * 10, 40)
        reasons.append(f"skills: {', '.join(skill_matches[:3])}")

    # === WORK TYPE ===
    work_matches = [kw for kw in WORK_TYPE_KEYWORDS if kw in searchable]
    if work_matches:
        score += min(len(work_matches) * 5, 15)

    # === URGENCY ===
    urgency_matches = [kw for kw in URGENCY_KEYWORDS if kw in searchable]
    if urgency_matches:
        score += 15
        reasons.append("urgent")

    # === POPULARITY (GitHub stars) ===
    stars = opportunity.get("stars", 0)
    if stars > 1000:
        score += 15
    elif stars > 100:
        score += 5

    # === PENALTY for unpaid/volunteer ===
    penalty_matches = [kw for kw in PENALTY_KEYWORDS if kw in searchable]
    if penalty_matches:
        score -= 50
        reasons.append(f"⚠️ {', '.join(penalty_matches[:2])}")

    # === FRESHNESS DECAY ===
    found_str = opportunity.get("found") or opportunity.get("created") or opportunity.get("scored_at")
    if found_str:
        try:
            found_date = datetime.fromisoformat(found_str.replace("Z", "+00:00").split("+")[0])
            age_days = (datetime.now() - found_date).days
            if age_days > 14:
                score -= 20
                reasons.append("stale (>14d)")
            elif age_days > 7:
                score -= 10
        except (ValueError, TypeError):
            pass

    return {
        **opportunity,
        "score": max(score, 0),
        "reasons": reasons,
        "scored_at": datetime.now().isoformat(),
    }


def rank_opportunities(opportunities):
    """Score and rank a list of opportunities."""
    skills = _load_user_skills()
    scored = [score_opportunity(opp, skills) for opp in opportunities]
    scored.sort(key=lambda x: x["score"], reverse=True)

    data = _load_scores()
    data["scored"].extend(scored)
    data["scored"] = data["scored"][-500:]
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
            data["dismissed_urls"] = data["dismissed_urls"][-200:]
            _save_scores(data)
        return active[index]
    return None


def log_earning(amount, source, description=""):
    """Log an earning (manual tracking via /earned command)."""
    data = _load_scores()
    entry = {
        "amount": amount,
        "source": source,
        "description": description,
        "date": datetime.now().isoformat(),
    }
    data.setdefault("earnings_log", []).append(entry)
    _save_scores(data)
    return entry


def get_earnings_summary():
    """Get earnings summary for different time periods."""
    data = _load_scores()
    earnings = data.get("earnings_log", [])
    now = datetime.now()

    totals = {"today": 0, "week": 0, "month": 0, "all_time": 0}
    for e in earnings:
        amount = e.get("amount", 0)
        try:
            date = datetime.fromisoformat(e["date"])
            age = now - date
            totals["all_time"] += amount
            if age.days < 1:
                totals["today"] += amount
            if age.days < 7:
                totals["week"] += amount
            if age.days < 30:
                totals["month"] += amount
        except (ValueError, KeyError):
            totals["all_time"] += amount

    return totals


def format_scored_report(scored, limit=5):
    """Format top scored opportunities for Telegram."""
    if not scored:
        return "No scored opportunities yet."

    if isinstance(scored, list):
        top = sorted(scored, key=lambda x: x.get("score", 0), reverse=True)[:limit]
    else:
        top = [scored]

    msg = "*🏆 Top Opportunities*\n\n"
    for i, opp in enumerate(top):
        title = opp.get("title", opp.get("name", "Untitled"))[:100]
        source = opp.get("source", "Unknown")
        score = opp.get("score", 0)
        url = opp.get("url", "")
        reasons = " | ".join(opp.get("reasons", [])[:3])

        msg += f"*{i+1}. \\[{source}] {title}*\n"
        msg += f"   Score: *{score}*"
        if reasons:
            msg += f" — {reasons}"
        msg += "\n"
        if url:
            msg += f"   {url}\n"
        msg += "\n"

    return msg


def format_earnings_report():
    """Format earnings summary for Telegram."""
    totals = get_earnings_summary()
    msg = "*💰 Earnings Summary*\n\n"
    msg += f"Today: *${totals['today']:,.2f}*\n"
    msg += f"This week: *${totals['week']:,.2f}*\n"
    msg += f"This month: *${totals['month']:,.2f}*\n"
    msg += f"All time: *${totals['all_time']:,.2f}*\n"
    return msg
