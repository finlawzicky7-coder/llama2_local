# Product Spec — Ringback MVP

Owner: Product Architect Agent. Reviewed by Engineering, AI Automation,
and QA Agents.

This document describes the **MVP** scope only. Anything labeled "post-MVP"
will not ship in Cycle 1.

---

## 1. Product Summary

Ringback is a multi-tenant SaaS that turns inbound missed calls into
booked jobs via an AI voice + SMS agent backed by a Postgres data plane.
A contractor signs up, forwards their phone line, and within 24 hours is
seeing recovered bookings.

## 2. User Roles

| Role        | Lives in                  | Capabilities                                    |
|-------------|---------------------------|-------------------------------------------------|
| Owner       | Tenant `users` table      | Full tenant admin: billing, members, settings   |
| Dispatcher  | Tenant `users` table      | View calls/bookings, edit job status, no billing|
| End-customer| Not authenticated         | Receives SMS, answers AI voice agent            |
| Platform admin | `platform_admins` table | Cross-tenant support; never edits without audit  |

## 3. Core User Stories

### Owner onboarding
1. Owner clicks "Start free trial" on landing page.
2. Creates tenant, invites dispatcher (optional), enters company info.
3. Picks Twilio area code → system provisions number.
4. Configures: business hours, service ZIPs, job-type list, average
   ticket per job type, emergency keywords.
5. Sets up call forwarding from existing line (we provide step-by-step
   instructions per major U.S. carrier).
6. Connects Google Calendar (OAuth) for booking write-back.
7. Connects Stripe (Stripe Connect optional in v2; MVP uses platform Stripe).

### Inbound call (the main money path)
1. Customer calls contractor's existing number.
2. Carrier forwards to Ringback Twilio number on busy/no-answer.
3. Twilio voice webhook → Ringback `/voice/incoming`.
4. Ringback opens a streaming voice agent (LLM with function-calling tools)
   that:
   - Greets per tenant template ("Thanks for calling Acme HVAC…").
   - Captures: name, phone, address, ZIP, job type, urgency, preferred time.
   - Detects emergency keywords; routes to tenant on-call number if matched.
   - Confirms qualification details back to caller.
   - Hangs up gracefully and dispatches to scheduler.
5. Scheduler tool:
   - Pulls next 3 available slots from Google Calendar.
   - Texts the caller via Twilio Messaging:
     "Hi {name}, this is {tenant.brand}. Earliest slots: A) Tue 10–12, B) Tue 2–4. Reply A or B."
6. Reply handler captures slot, writes a `booking` row, writes to Google
   Calendar, fires "new booking" webhook to Zapier, emails owner.

### SMS-only flow (if call drops or customer texts first)
- Twilio Messaging webhook → same agent state machine without voice.

### Daily digest
- 8am tenant-local time: email + dashboard digest of last 24h:
  calls handled, bookings created, missed/lost, transcripts.

## 4. Out of Scope for MVP

- Outbound calling. (Compliance work required before any outbound feature.)
- Native ServiceTitan/Jobber/Housecall Pro integrations beyond Zapier.
- Multi-location franchise dashboard. (Tier 3 stub only.)
- Spanish-language voice agent. (Tier 2 — feature-flagged, partial.)
- iOS/Android apps. (PWA only.)
- Self-serve price-book quoting. (Manual entry by tenant for MVP.)

## 5. Architecture (high-level)

```
┌────────────┐   inbound voice/SMS    ┌─────────────────────────────┐
│   Twilio   ├───────────────────────▶│   FastAPI app (api/)        │
│ (numbers)  │   webhooks (signed)    │   Python 3.11               │
└────────────┘                        │                             │
        ▲                             │  /voice/incoming            │
        │ outbound TTS / SMS          │  /voice/stream  (websocket) │
        │                             │  /sms/incoming              │
        │                             │  /webhooks/stripe           │
        │                             │  /webhooks/calendar         │
        │                             └──────────────┬──────────────┘
        │                                            │
        │                                            ▼
┌────────────┐                          ┌─────────────────────────────┐
│  ElevenLabs│◀──────TTS optional───────│   Agent runtime             │
│ (voice)    │                          │   - State machine           │
└────────────┘                          │   - LLM (function calling)  │
                                        │   - Tools: schedule_lookup, │
                                        │     create_booking,         │
                                        │     send_sms,               │
                                        │     emergency_route         │
                                        └──────────────┬──────────────┘
                                                       │
                                                       ▼
                                        ┌─────────────────────────────┐
                                        │  Supabase Postgres          │
                                        │  (RLS, see schema.sql)      │
                                        └─────────────────────────────┘
                                                       │
                                                       ▼
                                        ┌─────────────────────────────┐
                                        │  Google Calendar API        │
                                        │  Stripe (subs + metered)    │
                                        │  Resend (email digests)     │
                                        │  Zapier (booking webhook)   │
                                        └─────────────────────────────┘
```

## 6. Tech Choices and Rationale

| Layer        | Choice                       | Why                                                    |
|--------------|------------------------------|--------------------------------------------------------|
| Backend      | FastAPI (Python 3.11)        | Fast iteration; LLM/agent ecosystem is Python-first.   |
| DB           | Supabase Postgres            | RLS + auth + storage in one; matches prompt mandate.   |
| Voice        | Twilio Programmable Voice    | Best US carrier coverage; cheapest A-attestation path. |
| SMS          | Twilio Messaging             | Same vendor as voice; toll-free or 10DLC.              |
| LLM          | Provider-agnostic via adapter| Default: a function-calling capable model. Swappable.  |
| TTS (opt.)   | ElevenLabs                   | Lower latency vs. baseline; gated behind feature flag. |
| Frontend     | Next.js (app router) + Tailwind | Operator dashboard. Static landing.                  |
| Auth         | Supabase Auth (email + OTP)  | Cheaper than Clerk for MVP.                            |
| Payments     | Stripe (subs + usage records)| Industry standard; supports per-booking metering.      |
| Hosting      | Fly.io (api) + Vercel (web)  | Both cheap, both push-button.                          |
| Observability| Logfire / OpenTelemetry      | Required because LLM agents fail in subtle ways.       |
| Email        | Resend                       | Cheap, simple API.                                     |

The full-stack engineering agent must avoid vendor lock-in where reasonable
(LLM provider behind an adapter; TTS optional; voice provider behind a
TwilioClient wrapper).

## 7. Data Model (summary; canonical SQL in `/supabase/schema.sql`)

Core tables (tenant-scoped via `tenant_id uuid not null` + RLS):

- `tenants` — id, name, brand, billing_email, plan, trial_ends_at.
- `users` — id, tenant_id, email, role, auth_user_id (Supabase auth FK).
- `phone_numbers` — id, tenant_id, twilio_sid, e164, area_code, status.
- `business_hours` — tenant_id, day_of_week, open_local, close_local, tz.
- `service_zips` — tenant_id, zip.
- `job_types` — id, tenant_id, label, avg_ticket_cents, emergency_keywords[].
- `calls` — id, tenant_id, twilio_call_sid, from_e164, to_e164, started_at, ended_at, status, recording_url, transcript_jsonb.
- `messages` — id, tenant_id, direction, twilio_message_sid, body, status.
- `customers` — id, tenant_id, name, phone_e164, address, zip, source.
- `bookings` — id, tenant_id, customer_id, call_id, job_type_id, scheduled_for, status, gcal_event_id, success_fee_charged.
- `digests` — id, tenant_id, period_start, period_end, payload_jsonb, sent_at.
- `events` — append-only audit log (id, tenant_id, actor, kind, payload_jsonb).
- `platform_admins` — admin allow-list.
- `subscriptions` — id, tenant_id, stripe_subscription_id, plan, status.
- `usage_records` — id, tenant_id, kind ('booked_job' | 'minute'), qty, billed_at.

Indexes:
- `calls(tenant_id, started_at desc)`
- `bookings(tenant_id, scheduled_for)`
- `messages(tenant_id, created_at desc)`
- `events(tenant_id, created_at desc)`

Constraints:
- `bookings.scheduled_for >= now() - 1 day` (sanity check).
- `customers.phone_e164` unique per tenant.
- All `tenant_id` columns have foreign keys with `on delete restrict`.

## 8. Build Sequence (Day-by-Day)

| Day | Owner               | Output                                                                |
|-----|---------------------|-----------------------------------------------------------------------|
| 1   | Validation Agent    | 150 outbound, 8+ booked calls, go/no-go memo                          |
| 2   | Product Architect   | This doc; schema.sql; rls-policies.sql; agent state diagram           |
| 3   | Engineering Agent   | FastAPI scaffold; Twilio voice/sms webhook; Supabase migrations apply |
| 3   | AI Automation Agent | Agent state machine; tool schemas; LLM adapter; tests                 |
| 4   | Engineering Agent   | Stripe sub + metered billing; Google Calendar OAuth; digest email     |
| 4   | Frontend Agent      | Next.js dashboard (tenants, calls, bookings, settings)                |
| 5   | QA Agent            | Run launch readiness checklist; create bug list; fix-loop with eng    |
| 6   | Growth Agent        | Landing page live; demo audio; outbound campaign launched             |
| 7   | CEO-Orchestrator    | Onboard first 3 paid pilots; close validation loop                    |

## 9. Definition of Done for MVP

- Inbound call from a real cell phone is answered by the AI agent and
  produces a `bookings` row + Google Calendar event for at least one
  test tenant. (Verified in `qa-report.md`.)
- SMS-only flow produces the same `bookings` row.
- Stripe subscription created; per-booking usage record posts on each
  successful booking.
- Daily digest email delivered to test tenant at 8am local.
- RLS verified: no cross-tenant data leakage in any tested query.
- All Twilio webhooks verify signature.
- All env vars documented in `.env.example`.
- No `TODO` blockers in critical path code.
- One real cold-outbound recipient paid the trial activation.
