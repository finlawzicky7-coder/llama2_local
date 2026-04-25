# Autonomous Company Factory — Master Plan

This repository hosts the Autonomous Company Factory: a managed-agent studio
that identifies, validates, builds, launches, and improves profitable
autonomous micro-companies on a 7-day cadence.

The factory is run by a CEO-Orchestrator that delegates to 13 specialized
agents (see `/docs/agent-memory.md`). Every cycle produces concrete software,
funnels, automations, and operating playbooks — never just advice.

---

## 1. Mission

Ship one validated, revenue-capable micro-company per cycle, then compound
learnings into a reusable Company Factory Playbook so cycle N+1 is faster
and cheaper than cycle N.

## 2. Selected First Company — Ringback

**Codename:** Ringback
**One-liner:** "We answer the calls your crew can't, and book the job before
your competitor does."

**Category:** AI voice + SMS missed-call recovery for U.S. home-services
contractors (HVAC, plumbing, electrical, roofing, garage door, locksmith,
appliance repair, pest control).

**Scope guardrail:** Ringback handles **inbound** missed calls only. No
outbound cold-calling, no purchased lead lists, no SMS to consumers who did
not initiate contact. This eliminates almost all TCPA exposure and lets us
sell on a "common-carrier-style" assist narrative.

## 3. Why this company (scoring)

Scored 1–10 on the factory model (higher is better, except `compliance_risk`
and `competitive_weakness` which are inverted — high = good for us):

| Criterion                  | Score | Note                                                 |
|----------------------------|-------|------------------------------------------------------|
| Buyer pain                 | 10    | 30–62% of inbound contractor calls go unanswered     |
| Willingness to pay         | 9     | One recovered $500 job pays 3 months of subscription |
| Speed to MVP               | 9     | Twilio + LLM + scheduler + Stripe = days, not months |
| Ease of distribution       | 8     | Cold-email + Google Maps scrape + ServiceTitan partner play |
| Competitive weakness       | 7     | Incumbents (Numa, Goodcall) are bloated/expensive    |
| Automation potential       | 9     | The product *is* automation — agents call agents     |
| Gross margin               | 9     | ~85% after Twilio + LLM + Supabase                   |
| Compliance risk (inverted) | 8     | Inbound-only design sidesteps TCPA / DNC             |
| Founder advantage          | 8     | AI-native build; can ship LLM tooling faster         |
| Recurring revenue          | 9     | $249–$799/mo + per-booking success fee               |
| **Total**                  | **86/100** | Highest of the 9 candidates evaluated (see `market-research.md`) |

Runners-up (`STR cleaning ops`, `B2B data enrichment`, `insurance lead qual`,
`work order SaaS`) lost on speed-to-revenue, compliance, or competition.

## 4. Target Customer (ICP)

- **Firmographic:** U.S.-based home-services contractor, 1–25 trucks,
  $500K–$10M annual revenue, owner-operator or office manager makes the buy.
- **Behavioral:** Already on Google Local Services / Google Business Profile.
  Has at least one inbound number ringing into a cell phone or front desk.
  Misses calls during dispatch hours, lunch, evenings, and storm/peak load.
- **Tech baseline:** Uses one of {Jobber, Housecall Pro, ServiceTitan,
  Workiz, FieldEdge} or just Google Calendar + a notepad.
- **Trigger events:** Recent storm, recent hire, recent missed-job complaint,
  recent Google review mentioning "couldn't get through."

## 5. Core Pain

> "Every missed call is a $300–$2,000 job that just walked to my competitor.
> I don't have time to hire a receptionist, train them on my pricing, or
> babysit voicemail."

## 6. Paid Offer

**Tier 1 — Recover ($249/mo + $25/booked-job)**

- Inbound call forwarding via Twilio number or call-forwarding on busy/no-answer.
- AI voice agent answers, qualifies (job type, address, urgency), and
  texts back the customer with available time slots.
- SMS-first follow-up if voice fails or customer hangs up.
- Booking written to a shared calendar (Google) and the contractor's CRM via
  Zapier-grade integration when available.
- Daily missed-call digest to owner.

**Tier 2 — Recover Pro ($499/mo + $25/booked-job)**

- Everything in Tier 1, plus:
  - Two-way SMS with photo/address support.
  - Estimate-range quoting from a contractor-supplied price book.
  - After-hours emergency triage (route true emergencies to on-call number).
  - Spanish-language support.

**Tier 3 — Whitelabel ($799/mo flat)**

- Branded number/voice. Multi-location dashboard. Used by small franchise groups.

**Setup fee:** $0 (waived on annual). Annual = 2 months free.

## 7. MVP Scope (what we ship in 7 days)

The MVP is intentionally narrow. Anything not on this list is **out of scope**:

In:
1. Twilio inbound voice webhook → AI agent dialog → captures
   {name, phone, address, job_type, urgency, preferred_time}.
2. SMS fallback flow (Twilio Messaging) using the same state machine.
3. Booking write to a tenant-scoped Google Calendar via OAuth.
4. Daily email digest of missed calls + bookings.
5. Stripe subscription with 14-day trial; per-booking metered billing.
6. Tenant onboarding wizard (number provisioning, hours, job-type list,
   service area ZIPs, pricing book upload optional).
7. Operator dashboard: calls, transcripts, bookings, status.
8. RLS-backed Supabase Postgres for all tenant data.

Out (defer to v1.1 / v2):
- Multi-location franchise tooling.
- Estimate quoting from price book (Tier 2 — partial in MVP behind feature flag).
- Outbound win-back. (Compliance review required first.)
- CRM deep integrations beyond Zapier.
- Mobile app. (PWA only.)

## 8. Monetization

- $249 / $499 / $799 monthly subscriptions (Stripe).
- $25 per booked job, billed via Stripe usage records.
- Annual plans: 2 months free.
- Upsell: $99/mo "Reviews" add-on (post-job review request — already
  permission-based, so compliant).

**Unit economics target (see `agent-memory.md` for the model):**

- Twilio voice + SMS:           ~$0.025 / minute, ~$0.008 / SMS.
- LLM (function-calling agent): ~$0.06 / handled call avg.
- Supabase + infra:             ~$0.05 / call all-in at scale.
- Variable cost per call:       ~$0.18 average.
- COGS at 200 calls/mo/tenant:  ~$36.
- Tier-1 gross margin:          ~85%.

## 9. Launch Channel (first 90 days)

1. **Cold email + LinkedIn DM** to owner-operators in 5 metros (Phoenix,
   Dallas, Atlanta, Tampa, Charlotte). Sourced from Google Maps + state
   contractor license boards. ~30 messages/day per metro, manually
   reviewed (no scraping ToS violations, no purchased lists).
2. **Local services Facebook groups** — value-first posts + DMs only on opt-in.
3. **Partner play** — pitch one regional Jobber/Housecall Pro reseller
   for revenue share.
4. **Google Local Services Ads** — only after 5 paying customers prove ROI.

We are explicitly **not** launching with TikTok, X threads, or paid social
until paid pilots prove the offer.

## 10. Success Metrics (kill / ship gates)

| Phase            | Gate                                                    | Decision rule              |
|------------------|---------------------------------------------------------|----------------------------|
| Validation (D7)  | ≥ 8 booked discovery calls from 150 cold messages       | <4 booked → kill / pivot   |
| Pilot (D30)      | ≥ 5 paid pilot customers @ $249+                        | <3 paying → pivot offer    |
| Product (D45)    | ≥ 70% missed-call → answered-by-agent rate              | <50% → engineering rework  |
| Retention (D90)  | ≥ 80% logo retention, ≥ 1.0x net revenue retention      | <60% retention → kill      |
| Margin (D90)     | Gross margin ≥ 75% on Tier-1                            | <60% → reprice or kill     |

If ALL gates pass at D90, scale to 50 customers and start cycle N+2 in parallel.

---

See also:
- `/docs/market-research.md` — the full opportunity scan and competitor teardown.
- `/docs/validation-plan.md` — the 7-day demand test and exact scripts.
- `/docs/product-spec.md` — MVP architecture, user stories, and database design.
- `/docs/growth-plan.md` — 30-day acquisition system.
- `/docs/sales-playbook.md` — qualification, demo, and objections.
- `/docs/operations-sop.md` — onboarding, fulfillment, and support SOPs.
- `/docs/qa-report.md` — the launch readiness checklist (currently un-passed).
- `/docs/decision-log.md` — every CEO-Orchestrator decision with reasoning.
- `/docs/agent-memory.md` — agent rosters, prompts, and reusable templates.
