# Autonomous Company Factory

A managed-agent studio that builds, validates, launches, and improves
profitable autonomous micro-companies on a 7-day cadence.

The CEO-Orchestrator agent runs the studio; 13 specialized agents do the
work. Cycle 1's selected first company is **Ringback** — an inbound
missed-call recovery service for U.S. home-services contractors.

This repository is the system of record for the factory: strategy docs,
agent prompts, decisions, schemas, and the production code that ships.

---

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

`.env.example` lists every secret the runtime expects. Copy to `.env`
and fill in before wiring real Twilio / Stripe / Supabase.

## Repo layout

```
docs/                    ← Strategy + decisions + playbooks (10 files).
supabase/
  schema.sql             ← Multi-tenant Postgres schema.
  rls-policies.sql       ← Deny-by-default row-level security.
src/ringback/            ← Pure-Python primitives, unit-tested.
  twilio_signing.py      ← HMAC-SHA1 Twilio webhook verification.
  redaction.py           ← PII redaction for logs.
  emergency.py           ← Emergency keyword detection.
  booking.py             ← Idempotent booking-key derivation.
  prompts.py             ← Voice/SMS agent prompt templates.
  agent_state.py         ← Pure state machine for the agent runtime.
app/                     ← FastAPI application (live runtime).
  main.py                ← App factory.
  config.py              ← Settings via pydantic-settings.
  voice.py               ← /voice/incoming, /voice/turn, /sms/incoming.
  billing_routes.py      ← /webhooks/stripe.
  dashboard.py           ← /, /healthz, /dashboard/{tenant_id}.
  twiml.py               ← TwiML response helpers.
  twilio_deps.py         ← Webhook signature dependency.
  call_state.py          ← Per-call session store.
  llm.py                 ← Provider-agnostic LLM adapter (Fake + HTTP).
  tools.py               ← Tools the agent can call (lookup, book, sms,
                            route_emergency, end_call).
  runtime.py             ← Drives the state machine through tool hops.
  repos.py               ← Repo interfaces + in-memory implementations.
  db.py                  ← asyncpg-backed repos (production).
  billing.py             ← Stripe port + Fake/HTTP impls.
  digest.py              ← Daily digest builder + email port.
  integrations/
    google_calendar.py   ← Google Calendar wrapper.
    resend_email.py      ← Resend email wrapper.
  deps.py                ← RuntimeBundle DI for routes + tests.
  types.py               ← Domain dataclasses.
tests/                   ← 63 unit + route tests (all offline).
.github/workflows/ci.yml ← pytest on every push.
Dockerfile               ← Production image.
Makefile                 ← `make install` / `make test` / `make run` / `make db-apply`.
.env.example             ← Every secret the runtime expects.
```

## Agent Task Board (Cycle 1)

Format per the master prompt:
`Agent / Task / Expected Output / Sequence / Dependencies / Definition of Done`.

| Agent | Task | Expected Output | Seq | Dep | Definition of Done |
|---|---|---|---|---|---|
| Market Intelligence | Opportunity scan + competitor teardown | `docs/market-research.md` | D1 | – | Top-10 ranked, persona, pain matrix, ≥3 competitors torn down |
| Finance | Score top-10, model unit economics | `agent-memory.md` §6 | D1 | Market | COGS + margin per tier; break-even count |
| Legal & Compliance | Risk register | `market-research.md` §8 + `agent-memory.md` §7 | D1 | Market | TCPA, recording, CAN-SPAM, PII rules documented |
| CEO-Orchestrator | Select first company + record decision | `decision-log.md` DL-001..007 | D1 | Market, Finance, Legal | Decision posted with alternatives + reason |
| Validation | Outbound test, discovery scripts, go/no-go | `docs/validation-plan.md` | D1 | CEO selection | 150 sent → ≥8 booked or kill |
| Growth | Offer, positioning, 30-day plan | `docs/growth-plan.md` | D1 | Validation | Hero offer, channel plan, KPIs, compliance guardrails |
| Sales Closer | Qualification, scripts, objection bank | `docs/sales-playbook.md` | D1 | Growth | BANT, scoring, 9 objections, follow-up sequence |
| Product Architect | MVP scope, architecture, schema | `docs/product-spec.md`, `supabase/schema.sql` | D2 | Validation passes | Schema applies; user stories complete |
| Engineering | Pure-Python primitives + tests | `src/ringback/`, `tests/` | D2 | Architect | `pytest -q` green |
| AI Automation | Tools, prompts, state machine | `src/ringback/{prompts,agent_state}.py`, `agent-memory.md` §3-§4 | D2 | Architect | State machine total; tool schemas in memory file |
| Operations | SOPs for onboarding, support, incidents | `docs/operations-sop.md` | D2 | Architect | 8 SOPs + dashboards spec |
| QA & Security | Launch checklist + RLS policies | `docs/qa-report.md`, `supabase/rls-policies.sql` | D2-D5 | All | All ✅ before launch — currently 28/100 |
| Memory & Documentation | Append decision log + agent memory | `docs/decision-log.md`, `docs/agent-memory.md` | D1-D7 | All | Every decision captured; templates reusable |
| Analytics | KPI tree + event taxonomy | `agent-memory.md` §8 | D2 | Architect | North-star defined; events listed |
| Engineering | Wire FastAPI + Twilio webhooks (live) | `app/`, deploy | D3 | Scaffold | Real call answered by AI agent |
| Engineering | Stripe subs + metered booking fee | `app/billing.py`, deploy | D4 | D3 | One usage record posted on booking |
| Engineering | Google Calendar OAuth + write-back | `app/calendar.py` | D4 | D3 | Booking creates GCal event |
| Frontend | Next.js operator dashboard | `web/` | D4 | D3 | Tenant can see calls + bookings |
| Growth | Landing page live + demo audio + outbound launch | hosted site | D6 | D3 voice working | Landing live; first 100 outreach sent |
| CEO-Orchestrator | Onboard 3 paid pilots; close validation | tenant rows | D7 | All | ≥3 paying, ≥1 recovered job, no Sev-1 |

## 7-Day Build Roadmap

| Day | Focus                   | Owner(s)                                   | Output                                                        |
|-----|-------------------------|--------------------------------------------|---------------------------------------------------------------|
| 1   | Research + validation   | Market, Finance, Legal, Validation, Growth | Strategy docs; first 50 outbound; landing copy draft          |
| 2   | Architecture            | Product Architect, Engineering, AI Auto    | This commit (schema, RLS, scaffold, prompts, state machine)   |
| 3   | Core build              | Engineering, AI Automation                 | FastAPI + Twilio voice/SMS webhooks; agent runtime online     |
| 4   | Automations + integrations | Engineering, AI Automation               | Stripe billing; Google Calendar write-back; digest email      |
| 5   | QA + fixes              | QA & Security, Engineering                 | Launch readiness ≥ 90/100; RLS verified end-to-end            |
| 6   | Launch assets           | Growth                                     | Landing live; demo audio; outbound at 100/day                 |
| 7   | First customer sprint   | CEO-Orchestrator, Sales, Operations        | ≥ 3 paid pilots; first recovered booking; close cycle 1 loop  |

## Quality Bar (must pass before launch)

- App must run end-to-end. (See `docs/qa-report.md` §2.)
- Core flows verified on a real cell phone calling a real Twilio number.
- No white screens, fake buttons, or dead pages in the dashboard.
- All secrets in `.env.example`; no hard-coded keys.
- Webhook signatures verified.
- RLS verified by end-to-end tenant-isolation test.
- Stripe usage record posts on booking.
- No untested critical path.

The QA agent is the launch gate — see `docs/qa-report.md` for the live
status. As of this commit: **28/100, NOT launch-ready.**

## Operating Rules (apply to every agent)

1. Don't pretend something is complete unless it is tested.
2. Don't remove working functionality unless replacing it with something
   clearly better.
3. Prefer simple, profitable, shippable systems over bloated architecture.
4. Every decision must be tied to evidence, assumptions, or test results.
5. Protect customer data, secrets, and PII at all times.
6. Never build illegal, deceptive, spammy, or policy-violating systems.
7. Inbound-only product mandate (Ringback specific — see DL-002).

## What's in this branch

- All 10 strategic docs filled out for Ringback.
- Multi-tenant Postgres schema + deny-by-default RLS policies.
- Pure-Python primitives (signing, redaction, emergency detection,
  booking idempotency, prompts, agent state machine).
- **Live FastAPI app** with Twilio voice + SMS webhooks, agent runtime,
  Stripe billing webhook, server-rendered operator dashboard, and a
  daily-digest builder.
- Provider-agnostic LLM adapter (`app/llm.py`) — `FakeLLMClient` for
  tests; `HTTPLLMClient` configured via `LLM_BASE_URL` + `LLM_API_KEY` +
  `LLM_MODEL` (any OpenAI-compatible endpoint).
- Asyncpg-backed Postgres repos (`app/db.py`) + in-memory repos for
  tests (`app/repos.py`).
- Google Calendar wrapper, Resend email wrapper, Stripe SDK wrapper —
  each behind a port with a `Fake*` implementation for offline tests.
- **63/63 tests passing** offline (unit + route).
- GitHub Actions workflow runs `pytest -q` on every push.
- Dockerfile + Makefile.

DL-008 (founder override) authorized building live integrations before
the validation gate (DL-005). The integrations are in place; running
the validation outbound and onboarding the first paid pilot are the
remaining steps to actually start the company.

## What still needs production wiring (and why)

- Live Postgres + Supabase project: apply `supabase/schema.sql` and
  `supabase/rls-policies.sql` (or `make db-apply`), then verify RLS
  isolation against a real auth user.
- Live Twilio number + carrier forwarding from a real contractor's line.
- Real LLM provider creds (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`).
- Real Stripe customer + booking-fee meter id.
- Per-tenant Google OAuth token storage + refresh.
- Real cold-outbound run (the validation step) per `validation-plan.md`.
- One real cell phone → real Twilio number → AI agent → booking → GCal
  event → Stripe usage record. The QA report tracks this as item 20.

## Final Cycle-1 Report

See `docs/qa-report.md` and `docs/decision-log.md`. Summary:

- **Built:** 10 strategy docs, schema + RLS, agent state machine + prompts,
  Twilio signature verifier, PII redactor, emergency detector, booking
  idempotency, 39 passing unit tests, agent task board, 7-day roadmap.
- **Tested:** every Python module via pytest; SQL parsed locally for
  syntax. RLS not yet applied to a live DB.
- **Failed initially:** state machine had a spurious DETECT_EMERGENCY
  state that consumed an utterance; emergency word-boundary test asserted
  the inverse of the design. Both fixed in-commit.
- **What still needs work:** D3–D7 of the roadmap (live integrations,
  validation outbound, paid pilots).
- **Next 10 highest-leverage actions:**
  1. Run validation outbound (150 messages) per `validation-plan.md`.
  2. Stand up FastAPI + Twilio voice webhook against the schema.
  3. Wire LLM adapter behind `LLMClient` with a function-calling default.
  4. Implement `lookup_open_slots` + `create_booking` tools end-to-end.
  5. Apply schema + RLS to a real Supabase project; run isolation tests.
  6. Stripe subscription + metered usage record for `booked_job`.
  7. Google Calendar OAuth + write-back.
  8. Build the operator dashboard (Next.js) and digest email.
  9. Record demo audio; launch landing page; send first 100 outreach.
  10. Onboard pilot #1 via SOP-1; capture full event log; close the loop.
