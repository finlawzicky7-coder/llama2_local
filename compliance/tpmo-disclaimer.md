# TPMO Disclaimer — Authoritative Wording

> Source of truth. Every place that displays the disclaimer pulls from this file by version. Never edit a published version in place — bump the version, update the placement, and run the daily audit (workflow 10) until the new version is live everywhere.

## Current canonical version: `tpmo-2026-04-01-v3`

> "We do not offer every plan available in your area. Currently we represent {N_CARRIERS} organizations which offer {N_PLANS} products in your area. Please contact Medicare.gov, 1-800-MEDICARE, or your local State Health Insurance Assistance Program (SHIP) to get information on all of your options."

`{N_CARRIERS}` and `{N_PLANS}` are dynamic and must reflect *current* contracted counts at the time the disclaimer is rendered. Use the most accurate count available; if you're unsure, default to "multiple" rather than a number that you can't substantiate.

## Where it must appear

| Surface | Placement | How |
|---|---|---|
| Landing pages | Above the fold, visible without scrolling on mobile | `<div class="tpmo-disclaimer" data-version="...">` |
| Landing-page footer | Footer, every page | `<p class="footer-tpmo">` |
| Sales call (outbound) | Within first 60 seconds | TwiML IVR before agent bridge |
| Sales call (inbound) | Within first 60 seconds | Auto-attendant prompt |
| Voice AI confirmation call | Opening greeting | Voice agent prompt |
| Email — every send | Footer | Postmark template footer block |
| SMS — every templated send | (Truncated) "Not Medicare. We don't offer every plan in your area. Reply STOP." | Template body |
| Print (direct mail) | Compliance area, ≥ 10pt font | Layout |
| YouTube video | Verbal in opening 30 s + on-screen text the entire duration | Edit + caption |
| Meta / Google ad copy | In ad headline or description, depending on space | Ad copy |
| Chat widget | First assistant message | `chat-v1` prompt |

## Versioning rules

- Bump version on **any** wording change, even punctuation. Compliance reviews diffs.
- The version string is `tpmo-YYYY-MM-DD-vN` — the date is when compliance signed off, not when it ships.
- When a new version goes live:
  - Landing-page deploy updates `data-version`.
  - n8n env vars `TPMO_VERSION_ACTIVE` updates.
  - Postmark / SMS templates are duplicated with new aliases (`appt_confirmation_v2`, etc.).
  - Workflow 10 includes a check that detects mismatched versions across surfaces and emits an `event_type='tpmo_version_drift'` warning.

## When to re-issue

- CMS issues new MCMG guidance with revised disclaimer language.
- Your contracted carrier count changes materially.
- You add or remove a state where you operate.
- The state insurance department in any state where you operate adopts a more stringent rule.

## Past versions (kept for audit only)

- `tpmo-2024-10-01-v1` — initial build.
- `tpmo-2025-04-15-v2` — added "or your local SHIP" link.
- `tpmo-2026-04-01-v3` — current.

## DO NOT

- Translate without a compliance-reviewed translation.
- Move it below the fold.
- Hide it inside an accordion or a tooltip.
- Combine it with "we represent the best plans" or any superlative that contradicts "we don't offer every plan."
- Use a smaller font than the surrounding body copy.
- Color it grey on grey or otherwise visually de-emphasize it.
