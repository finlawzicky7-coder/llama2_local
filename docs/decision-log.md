# Decision Log

Append-only. Every entry has a date, the decider (always CEO-Orchestrator
in cycle 1), the decision, the alternatives considered, and the reason.

---

## 2026-04-25 — DL-001 — Cycle 1 first company is Ringback

**Decider:** CEO-Orchestrator
**Decision:** Build Ringback (inbound missed-call recovery for U.S. home-services SMBs).
**Alternatives:** Medspa appointment-setter (#2), STR cleaning ops (#3),
insurance lead qualification (#4).
**Reason:** Highest score on the factory scoring model (86/100). Lowest
compliance risk thanks to inbound-only design. Fastest plausible path to
revenue (~7 days to first paid pilot). Architecture (Twilio + LLM + Supabase
+ Stripe) is reusable for #2 and #4 if cycle-2 reuses cycle-1 spine.
**Source:** `docs/market-research.md` §1, §2.

## 2026-04-25 — DL-002 — Inbound-only product mandate

**Decider:** CEO-Orchestrator (with Legal & Compliance Agent concurrence)
**Decision:** No outbound voice or SMS in MVP, full stop. Outbound is
not a roadmap item until a separate compliance review passes.
**Alternatives:** Build outbound win-back behind a feature flag.
**Reason:** TCPA exposure is severe; the value prop already pays for
itself without outbound; we keep our STIR/SHAKEN attestation clean.

## 2026-04-25 — DL-003 — Pricing: $249 / $499 / $799 + $25 per booked job

**Decider:** CEO-Orchestrator (with Finance Agent + Sales Agent concurrence)
**Decision:** Per-booking success fee ($25) on top of subscription.
**Alternatives:** Pure subscription; pure usage; per-minute (Smith.ai-style).
**Reason:** Per-booking aligns price with value, lowers buyer perceived
risk, and exposes Ringback's premium upside on busy contractors.
Pure-subscription tested poorly in informal pre-validation conversations
(buyer commodifies the price). Per-minute creates burst-cost anxiety.

## 2026-04-25 — DL-004 — LLM provider behind an adapter

**Decider:** CEO-Orchestrator
**Decision:** Code targets a thin internal `LLMClient` adapter; the
default implementation is provider-agnostic and configured by env var.
**Alternatives:** Hard-code to a single provider for speed.
**Reason:** Voice latency tuning will require A/B'ing models; we don't
want to be locked in. Adapter cost is minimal.

## 2026-04-25 — DL-005 — Validation gate before MVP build

**Decider:** CEO-Orchestrator
**Decision:** No code beyond architecture + schema + scaffold until
Validation Agent reports ≥ 8 booked discovery calls in 7 days.
**Alternatives:** "Build and they will come" — rejected.
**Reason:** Operating rule "Don't pretend something is complete unless
it is tested." Same logic applies to demand: don't ship a product unless
demand is tested.

## 2026-04-25 — DL-006 — Use Supabase Postgres with RLS as the single data plane

**Decider:** CEO-Orchestrator
**Decision:** All tenant data lives in Supabase Postgres with RLS.
**Alternatives:** Bring-your-own-Postgres + custom auth.
**Reason:** RLS is the cheapest robust multi-tenant safety net; Supabase
gives us auth + storage + cron in one bill. Avoids re-implementing
session security on day 1.

## 2026-04-25 — DL-007 — Repository scope: this branch is planning + scaffold, not a deployable MVP

**Decider:** CEO-Orchestrator
**Decision:** This commit delivers the Company Factory plan, agent roster,
Ringback strategic docs, Supabase schema + RLS, and a runnable Python
scaffold with unit tests. It does NOT claim to be a production MVP.
The QA launch checklist is intentionally listed as un-passed in
`qa-report.md` to keep us honest under the operating rule "Do not pretend
something is complete unless it is tested."
**Alternatives:** Push a half-built end-to-end MVP and call it done.
**Reason:** Honesty > theatre. The next cycle of work (D3–D5 in the
roadmap) is what produces the deployable artifact.
