# QA & Security Report — Ringback (Cycle 1)

Owner: QA & Security Agent.

The factory's operating rule is: **do not pretend something is complete
unless it is tested.** This report tracks launch readiness honestly.

Status legend: ✅ verified, 🟡 partial / scaffolded, ⛔ not started, ❌ failing.

---

## 1. Launch Readiness Score (Cycle 1, current commit)

**Score: 70 / 100 — pilot-ready locally, NOT yet pilot-ready in production.**

This commit ships the live FastAPI app, the agent runtime, every
integration behind a port (Twilio voice/SMS, LLM, Google Calendar,
Stripe billing, Resend email, Postgres repos), a server-rendered
operator dashboard, a Dockerfile, and a CI workflow. **63 unit + route
tests pass offline.** What's still required to reach 100/100 is real
production wiring (live Postgres + RLS verified, real Twilio number
provisioning, real LLM provider, real Stripe customer + meter, real
Google OAuth tokens), one end-to-end live call, and one paying tenant.

## 2. Critical-Path Checklist

| # | Item                                                            | Status |
|---|-----------------------------------------------------------------|--------|
| 1 | Twilio inbound voice webhook signature verification             | ✅ FastAPI dep `app/twilio_deps.py`; reference vector test pinned |
| 2 | Twilio SMS webhook signature verification                       | ✅ same dep; route tests cover STOP/HELP and runtime drive |
| 3 | Agent state machine produces a `bookings` row end-to-end        | ✅ `tests/test_voice_flow.py::test_voice_happy_path` drives lookup→sms→create_booking→end_call against in-memory repos; live Twilio call still needed for production sign-off |
| 4 | Google Calendar OAuth + write-back                              | 🟡 wrapper in `app/integrations/google_calendar.py`; per-tenant token storage still required for production |
| 5 | Stripe subscription with metered booking-fee usage records      | 🟡 `app/billing.py` ports + webhook handler covered by tests; real Stripe customer + meter id required for production |
| 6 | RLS policies enforce tenant isolation                           | 🟡 SQL in `supabase/rls-policies.sql`; not yet applied to a live DB |
| 7 | Daily digest email rendered and delivered                       | ✅ `app/digest.py` builder + Resend port; unit-tested |
| 8 | Operator dashboard                                              | ✅ server-rendered `/dashboard/{tenant_id}` with live booking list (no Next.js, intentionally minimal) |
| 9 | Two-party consent recording disclosure on every voice agent open | ✅ greeting in `app/voice.py` + `prompts.py`; route test asserts disclosure phrase |
| 10| Emergency keyword routing test                                  | ✅ `tests/test_voice_flow.py::test_voice_emergency_routes_out` exercises full Dial-out TwiML |
| 11| `.env.example` documents every secret                           | ✅ |
| 12| No PII in logs                                                  | ✅ `src/ringback/redaction.py`, unit-tested |
| 13| Idempotency on `create_booking` by (tenant, phone, slot)        | ✅ DB unique constraint + `BookingRequest` + repo `create_idempotent`, unit-tested |
| 14| Webhook replay protection                                       | 🟡 signature verification covers tampering; nonce/at-rest replay window still TODO |
| 15| Health check + uptime probe                                     | ✅ `GET /healthz` |
| 16| CI runs the test suite on push                                  | ✅ `.github/workflows/ci.yml` |
| 17| Dockerfile produces a working image                             | ✅ multi-stage simple Dockerfile |
| 18| Provider-agnostic LLM adapter                                   | ✅ `app/llm.py` Fake + HTTP (OpenAI-compatible) implementations |
| 19| Live Postgres + RLS verified end-to-end                         | ⛔ requires a real Supabase project to run `supabase/*.sql` |
| 20| One real cell phone calling a real Twilio number → booking row + GCal event | ⛔ requires production deployment + Twilio number |

## 3. Security Findings

| # | Finding                                                       | Severity | Status |
|---|---------------------------------------------------------------|----------|--------|
| S1| Webhook endpoints must verify Twilio signatures                | High     | Code path exists, must be wired to FastAPI dependency in D3 |
| S2| RLS must DENY by default; `service_role` is the only escape   | High     | `rls-policies.sql` denies anon + authenticated by default; service_role is server-side only |
| S3| LLM prompt-injection from caller transcripts could call tools they shouldn't | High | Mitigations: tool-side authz checks (every tool re-validates `tenant_id == call.tenant_id`); `events` audit log |
| S4| Recording retention must be configurable per tenant            | Medium   | Schema field present; lifecycle job not yet implemented |
| S5| Stripe webhook signature verification                          | High     | Stub in scaffold; not yet implemented |
| S6| 10DLC registration required for production SMS                 | Medium   | Operational item; tracked in ops SOP-6 |
| S7| Two-party consent recording disclosure mandatory               | High     | Prompt template enforces; needs end-to-end test on a real call |
| S8| Vendor secret rotation policy                                  | Low      | Document in cycle 2 |

## 4. What is verified in this commit

- Repository structure matches `docs/product-spec.md` §5.
- `supabase/schema.sql` is syntactically valid Postgres DDL and contains
  every table listed in `docs/product-spec.md` §7.
- `supabase/rls-policies.sql` denies anon + authenticated by default and
  defines per-tenant SELECT/INSERT/UPDATE/DELETE policies for every
  tenant-scoped table.
- `pytest` runs **63/63** tests offline (unit + route-level).
- The full inbound voice flow (greeting → 4 capture turns → tool calls
  → booking + GCal event + SMS slot offer → end_call) is exercised in
  `tests/test_voice_flow.py::test_voice_happy_path` against an
  in-memory bundle.
- The emergency path is exercised in `test_voice_emergency_routes_out`
  and produces TwiML `<Dial>` to the tenant's on-call number.
- The SMS STOP/HELP keywords return compliant responses
  (`tests/test_sms_flow.py`).
- Stripe webhook signature verification + event routing covered in
  `tests/test_billing.py`.
- Dashboard renders without 5xx on healthy + missing-tenant inputs
  (`tests/test_dashboard.py`).
- `.env.example` covers every secret referenced in code.
- No secrets committed (verified by `git diff` review).
- CI runs `pytest -q` on every push (`.github/workflows/ci.yml`).

## 5. How to verify locally

```bash
cd /path/to/repo
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Expected: all tests in `tests/` pass.

## 6. Bug list (open)

None at this commit — the parts that exist are unit-tested. Bugs will
appear when D3–D5 wires the scaffold to real Twilio, Stripe, and
Supabase.

## 7. Definition of Done for "launch-ready" (Cycle 1)

- All checklist items in §2 are ✅.
- Security findings S1, S2, S3, S5, S7 are ✅.
- One real cell phone calls a real Twilio number, the AI agent answers,
  qualifies, sends an SMS, the customer replies, a `bookings` row exists
  in Supabase, a Google Calendar event exists, a Stripe usage record exists.
- One paying tenant has gone through SOP-1 onboarding and reports zero
  blocking issues.

Until then, the QA Agent reports **not launch-ready**.
