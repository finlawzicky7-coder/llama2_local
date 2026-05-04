# Scaling Roadmap

A staged plan from MVP to multi-state, multi-channel, multi-agent operation. Compliance posture is non-negotiable at every stage; only the breadth and depth changes.

## Stage 0 — Foundations (weeks 1–4)

**Goal:** running, auditable, single-state, single-agent end-to-end.

- Deploy Supabase migrations 0001–0006.
- Deploy n8n with workflows 01–11.
- Deploy 1 landing page (`medicare-review.html`) for 1 state.
- Wire Twilio with 1 DID, 10DLC SMS, voicemail drop, recording bucket.
- One licensed agent in one state; one carrier appointment.
- Run 10 synthetic leads end-to-end; verify every audit dimension.
- Run 10 friend-and-family real leads with explicit consent; verify recordings, disclaimers, opt-outs.

Exit criteria: pre-launch checklist 100%, zero critical exceptions in audit logs over 7 days.

## Stage 1 — Single-state production (weeks 5–10)

**Goal:** reach $50/lead CPL with positive CPS in one state, evergreen.

- Spin up Google Search ads for 5–10 high-intent Medicare keywords in one metro.
- Local SEO: 10 city/county pages, all education-first, all carrying TPMO disclaimer.
- Direct mail QR code funnel for T65 (mail to 1k T65 households monthly).
- Add 2–3 more agents in the same state; capacity scaling tested.
- Monthly compliance review.
- Tune `fn_score_lead` weights against actual conversions.
- Establish source-quality baseline: connect rate by source, opt-out rate by source, close rate by source.

Exit criteria: 30 days of stable CPL, CPA, CPS; agent capacity not maxed; source-quality scores stable.

## Stage 2 — Multi-state (weeks 11–22)

**Goal:** 5–10 states; per-state DIDs; per-state agent rosters.

- Add states one at a time. For each state:
  - Confirm state-specific DNC, recording-consent, and marketing rules.
  - Onboard at least 2 licensed agents in the state.
  - Spin up state-specific DIDs and SMS senders.
  - Localize a landing page variant (`/medicare-review/{state-name-slug}`).
- Add YouTube education funnel: 3 evergreen videos per quarter; description carries disclaimer; on-screen disclaimer for full duration.
- Add Meta retargeting (educated audiences only — no cold Medicare audiences on Meta).
- Introduce skill-aware routing: T65 / Medigap / DSNP routing.
- Compliance officer hires a part-time auditor; weekly QA cadence on calls.

Exit criteria: state-level CPS within 1.2x of state-1 baseline; compliance flag rate flat.

## Stage 3 — AEP readiness (months 6–9, before Oct 15)

**Goal:** survive AEP without compliance findings; double normal volume cleanly.

- Pre-AEP audit: full pre-launch checklist re-run.
- Stress-test dialer at 3x current peak.
- Confirm DNC vendor capacity at AEP volume.
- Lock script and template versions 7 days before Oct 15; no AEP-eve changes.
- Pre-fund Twilio, Postmark, ad-platform balances.
- Hire seasonal call center capacity if needed; treat them exactly like full-time agents — same training, same recording, same RLS.
- Pre-AEP compliance training week-of for everyone.
- Daily compliance officer + on-call rotation through Dec 7.

Exit criteria: zero critical compliance events during AEP; 2x volume handled within capacity; rapid-disenrollment rate < industry average.

## Stage 4 — National + advanced AI (year 2)

**Goal:** 30+ states; multi-channel acquisition; predictive routing; carrier-specific funnels.

- Expand to all states where you can field at least 3 agents (avoid single-point licensing risk).
- Carrier-specific (when a partner carrier requests) education funnels — under that carrier's marketing review.
- Voice AI (`voice-v1`) for callback confirmations only (still no AI-led sales).
- Predictive scoring: replace `fn_score_lead`'s weights with a gradient-boosted model trained on close outcomes; keep the deterministic version as fallback.
- Lead-LTV model to feed bid management.
- Per-zip deliverability monitoring of outbound DIDs; auto-rotate flagged numbers.
- Quarterly external compliance audit (independent firm).

## Stage 5 — Channel diversification (year 3+)

**Goal:** owned vs paid lead mix tilts toward owned.

- Existing-client referral automation (workflow 12 candidate): post-enrollment day 30, ask for referral; SOA-aware; never share client's data without explicit referral consent.
- Community event funnels: senior centers, libraries, faith communities — with on-site disclaimer signage and event-specific consent forms.
- Local PR / earned media: become the trusted local voice on Medicare basics.
- Educational webinars (compliance-reviewed before each).
- Strategic partnerships with non-TPMO entities (financial planners, eldercare attorneys) under CMS-permitted referral structures.

## Things that do **not** scale (don't try)

- "Aggressive" outbound to cold-list data — TCPA risk grows non-linearly.
- AI-led enrollment calls — CMS scrutiny too high; recording reviewers expect a licensed human.
- Multi-TPMO bundled consent — CMS will find this and the cost is enormous.
- "Free benefits" or "savings up to" headlines as scale tactics — same.
- Buying lead lists from vendors who can't produce per-lead consent evidence with IP/UA/timestamp.

## Capacity planning rules of thumb

- 1 agent ≈ 30–40 quality conversations / day at AEP peak (~80–100 dial attempts).
- 1 compliance reviewer ≈ 50 calls/day on detailed review.
- 1 ops engineer per ~5 agents and ~3 states for n8n/Supabase health.
- DNC vendor + Twilio + LLM costs scale roughly with lead volume; budget 12–18% of CPL toward compliance/orchestration overhead.
