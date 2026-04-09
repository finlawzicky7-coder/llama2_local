# Phase 3 — Lead Routing

## Classification

Every captured form runs through `shared/lead-router.js#routeLead()`, which
returns `{ funnel_source, lead_score, upsell_funnel }`.

Priority order:
1. **Explicit source** — the landing page tells the router which funnel it is
   (`script.js` passes `'mtr'` or `'cleaning'`).
2. **Keyword match** — `service_interest` + `notes` are scanned with the
   CLASSIFIERS regex list.
3. **Fallback** — default to `mtr` (highest revenue per lead).

## Scoring

See `shared/lead-scoring.js`. Funnel-specific weights:

### MTR
| Signal | Points |
| --- | --- |
| Stipend ≥ $2,800 | +35 |
| Stipend ≥ $2,000 | +20 |
| Stipend ≥ $1,200 | +10 |
| City in target area | +20 |
| Valid phone | +15 |
| Keywords: travel nurse / contract / 13 week | +20 |
| Keywords: furnished / month | +10 |

### Cleaning
| Signal | Points |
| --- | --- |
| ≥ 400 turns/mo budget | +25 |
| ≥ 150 turns/mo budget | +15 |
| Any turnover budget | +5 |
| City in target area | +25 |
| Valid phone | +20 |
| Keywords: airbnb / STR / vrbo | +20 |
| Keywords: mid-term / monthly | +10 |

Score thresholds used by n8n:
- `≥ 70` → HOT: Slack alert, call within 5 min
- `40–69` → WARM: standard intro email + day 1/3/5 follow-ups
- `< 40` → COLD: drip sequence only

## Cross-funnel upsell

`crossFunnelUpsell()` detects obvious re-routes:
- Cleaning lead mentioning "multiple STRs" → trigger cohosting outreach
  (reserved for Phase 8 when cohosting launches).
- MTR lead with no budget but cleaning keywords → route to cleaning instead.

The upsell target is stored on the row (`raw_payload.upsell_funnel`) so a
future workflow can pick it up without re-running the router.
