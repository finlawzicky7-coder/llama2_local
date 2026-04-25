# Agent Memory — Company Factory

This file is the durable memory of the Autonomous Company Factory:
agent rosters, prompts, reusable templates, and lessons learned.

It is **append-only** in spirit. Update sections in place when better
templates are produced; never delete the older version — move it to
`/docs/archive/` and link from here.

---

## 1. Roster (Cycle 1)

| Agent                          | Owner area                                | Canonical doc(s)                          |
|--------------------------------|-------------------------------------------|-------------------------------------------|
| CEO-Orchestrator               | Strategy, sequencing, decisions           | `company-factory.md`, `decision-log.md`   |
| Market Intelligence Agent      | Opportunity scan, competitor teardown     | `market-research.md`                      |
| Validation Agent               | Demand testing                            | `validation-plan.md`                      |
| Product Architect Agent        | MVP scope, user stories, data model       | `product-spec.md`                         |
| Full-Stack Engineering Agent   | Code: backend, frontend, integrations     | `src/`, `app/`, `tests/`                  |
| AI Automation Agent            | Agent runtime, tools, prompts             | `src/ringback/agent.py`, `src/ringback/tools.py` |
| Growth Agent                   | Acquisition, positioning, copy            | `growth-plan.md`                          |
| Sales Closer Agent             | Pipeline, discovery, objections           | `sales-playbook.md`                       |
| Operations Agent               | Onboarding, support, dashboards, SOPs     | `operations-sop.md`                       |
| Finance Agent                  | Pricing, unit economics, forecast         | this file §6                              |
| Legal & Compliance Agent       | TCPA, CAN-SPAM, recording, PII            | `market-research.md` §8, this file §7     |
| QA & Security Agent            | Tests, regressions, RLS, launch checklist | `qa-report.md`                            |
| Analytics Agent                | KPI tree, events, dashboards              | this file §8                              |
| Memory & Documentation Agent   | This file. Decision log. Templates.       | this file                                 |

Each agent operates from a focused subset of context. Outputs are
always concrete files and rows in the Agent Task Board (`README.md`).

## 2. Reusable Agent Prompt Skeleton

```
You are the {Agent Name} for the Autonomous Company Factory.

Mission: {one-line mission}
Boundary: You produce concrete deliverables, not advice.
Inputs: {list of doc paths the agent should read first}
Outputs: {explicit list of artifacts and where they live}
Compliance: Re-read `/docs/market-research.md` §8 before any
            outbound or PII-touching deliverable.
Definition of Done: {bulleted, testable}
Escalate when: {bulleted situations that must go to CEO-Orchestrator}
```

## 3. Tool / Function Schemas (Ringback agent runtime — canonical)

The voice/SMS agent uses these tools. Schemas mirror the Python
implementations in `src/ringback/tools.py`.

### `lookup_open_slots(tenant_id, duration_minutes, earliest_after_iso)`
Returns up to N (default 3) open slots from the tenant's connected
calendar. Read-only. No side effects.

### `create_booking(tenant_id, customer, job_type, scheduled_for_iso, notes)`
Inserts a `bookings` row, writes a Google Calendar event, and triggers
the Zapier webhook. Idempotent on
`(tenant_id, customer.phone_e164, scheduled_for_iso)`.

### `send_sms(tenant_id, to_e164, body)`
Sends an SMS via Twilio Messaging. Auto-injects the tenant's STOP / HELP
footer on the first message of a thread.

### `route_emergency(tenant_id, call_sid)`
Bridges the inbound call to the tenant's on-call number. Writes an
`events` row of kind `emergency_routed`.

### `end_call(call_sid, summary)`
Ends the call gracefully and writes a transcript summary into `calls.transcript_jsonb`.

All tools log to the `events` table with the tenant id, the actor
(`agent` for the LLM, `human` for operators), and a JSON payload.

## 4. Agent State Machine (voice + SMS)

```
[greet]
  │
  ▼
[detect_emergency?] ── yes ──▶ [route_emergency] ──▶ [end_call]
  │ no
  ▼
[capture: name]
  │
  ▼
[capture: address + zip]
  │
  ▼
[capture: job_type]    ◀── tenant.job_types reference
  │
  ▼
[capture: urgency / preferred_window]
  │
  ▼
[lookup_open_slots]
  │
  ▼
[propose_slots_via_sms]   (voice: "we'll text you 3 times")
  │
  ▼
[await_sms_reply]   (timeout: 30 min → followup_sms; 24 h → mark lost)
  │
  ▼
[create_booking]
  │
  ▼
[end_call] / [end_thread]
```

## 5. Reusable Templates

### Cold email template
See `docs/validation-plan.md` §4 and §5.

### Discovery call template
See `docs/sales-playbook.md` §4.

### Onboarding checklist
See `docs/operations-sop.md` SOP-1.

### Decision-log entry
See any entry in `docs/decision-log.md`. Format:
`Decider / Decision / Alternatives / Reason / Source`.

### Post-mortem template (incident or kill decision)
- What happened
- Timeline
- Customer impact
- Root cause
- What we changed
- What we'll watch for next cycle

## 6. Finance — Cycle 1 Unit Economics (Ringback)

Assumptions used for the model in `company-factory.md` §8:

| Item                                      | Value                          |
|-------------------------------------------|--------------------------------|
| Avg inbound calls / tenant / month        | 200                            |
| Avg call length                           | 90 seconds                     |
| Twilio voice                              | $0.0085 / min inbound to TN    |
| Twilio SMS (10DLC)                        | $0.0079 / segment              |
| LLM cost / handled call (function-calling)| ~$0.06 (assumes ~3k tokens)    |
| ElevenLabs TTS (optional)                 | ~$0.04 / call (off by default) |
| Supabase + Fly + Vercel                   | $300/mo platform amortized at 100 tenants = $0.015/call |
| Variable cost / handled call              | ~$0.18                         |
| COGS / tenant / mo @ 200 calls            | ~$36                           |
| Tier 1 ($249) gross margin                | ~85%                           |
| Tier 2 ($499) gross margin                | ~88%                           |
| Booking fee ($25) margin                  | ~99%                           |

Break-even on a 1-founder team with $4k variable monthly cost (cloud +
LLM + Twilio float) ≈ 18 paid Tier-1 logos. Achievable within 60–90 days
*if* validation passes.

## 7. Compliance Reminders (Legal Agent canonical)

- **Inbound-only.** No outbound voice/SMS to a consumer who didn't
  initiate. (DL-002.)
- **Two-party consent.** Voice agent announces "this call may be
  recorded" before any audio is captured. CA, FL, IL, MA, MD, MT, NV,
  NH, PA, WA all matter; we apply the disclosure universally.
- **CAN-SPAM.** Cold email contains physical mailing address +
  unsubscribe link, honored same-day.
- **10DLC.** Production SMS senders must have brand + campaign registered.
- **PII.** No PII in logs (`logger.info` cannot include phone, address,
  full name). Use `events` table with explicit redaction policy.
- **Recordings retention.** Default 90 days; tenant can opt to 30 or 7
  days; deletions hard-delete the audio + transcript.
- **DPA.** Template lives in `/docs/legal/dpa-template.md` (post-MVP).

## 8. Analytics — KPI Tree (Ringback)

```
North Star: Recovered Booked Revenue / Tenant / Month
            = bookings_count * avg_ticket * close_rate
                    │              │              │
                    │              │              └─ pulled quarterly via tenant survey
                    │              └─ per tenant, set during onboarding
                    │
                    ├─ inbound_calls (Twilio events)
                    ├─ answered_by_agent_rate (calls / inbound_calls)
                    ├─ qualified_rate (qualifications / answered)
                    └─ booking_rate (bookings / qualifications)
```

Event taxonomy (canonical): `tenant.created`, `number.provisioned`,
`call.received`, `call.answered`, `call.qualified`, `call.lost`,
`call.emergency_routed`, `sms.sent`, `sms.replied`, `booking.created`,
`booking.gcal_synced`, `booking.canceled`, `digest.sent`,
`subscription.created`, `subscription.updated`, `subscription.canceled`,
`usage.booked_job`.

## 9. Lessons Learned (cycle log)

Append entries here at the end of each cycle. Each entry: date,
context, lesson, action.

(Empty until Cycle 1 completes.)

## 10. Cycle 1 Opportunity Log (raw scores)

Long-list scoring is in `docs/market-research.md` §1; raw rationale
notes used to generate that table can be kept here when added by the
Market Intelligence Agent. (Pending in this repo until cycle close.)
