"""Emergency keyword detection for the Ringback voice/SMS agent.

Tenants supply a list of emergency keywords per job type (e.g. HVAC:
"no heat in winter", "gas leak"). At runtime we match the caller's
transcribed utterance against the union of the tenant's emergency
keywords plus a small universal fallback set.

Match rules:
    - case-insensitive
    - whole-word match for short keywords (<= 5 chars) to reduce false
      positives like "no" → matching every utterance
    - substring match for keywords > 5 chars
    - special phrase "911" always triggers emergency routing
"""

from __future__ import annotations

import re
from typing import Iterable

_UNIVERSAL_EMERGENCY_TERMS = (
    "911",
    "fire",
    "flood",
    "flooding",
    "gas leak",
    "smell gas",
    "smoke",
    "sparks",
    "burning",
)


def _compile(terms: Iterable[str]) -> list[re.Pattern[str]]:
    patterns: list[re.Pattern[str]] = []
    for raw in terms:
        term = raw.strip().lower()
        if not term:
            continue
        if len(term) <= 5:
            patterns.append(re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE))
        else:
            patterns.append(re.compile(re.escape(term), re.IGNORECASE))
    return patterns


def is_emergency(utterance: str, tenant_keywords: Iterable[str] = ()) -> bool:
    """True when `utterance` matches any tenant or universal emergency term."""
    if not utterance:
        return False
    terms = list(tenant_keywords) + list(_UNIVERSAL_EMERGENCY_TERMS)
    for pat in _compile(terms):
        if pat.search(utterance):
            return True
    return False
