# QA & Security Report — Ringback (Cycle 1)

Owner: QA & Security Agent.

The factory's operating rule is: **do not pretend something is complete
unless it is tested.** This report tracks launch readiness honestly.

Status legend: ✅ verified, 🟡 partial / scaffolded, ⛔ not started, ❌ failing.

---

## 1. Launch Readiness Score (Cycle 1, current commit)

**Score: 28 / 100 — NOT launch-ready.**

This commit ships the planning artifacts, the data model, and a
runnable Python scaffold with unit tests. It does **not** ship a
deployable MVP. Below is the precise picture.

## 2. Critical-Path Checklist

| # | Item                                                            | Status |
|---|-----------------------------------------------------------------|--------|
| 1 | Twilio inbound voice webhook signature verification             | 🟡 scaffolded; verifier in `src/ringback/twilio_signing.py`, unit-tested |
| 2 | Twilio SMS webhook signature verification                       | 🟡 same module; unit-tested |
| 3 | Agent state machine produces a `bookings` row end-to-end        | ⛔ not yet — depends on real Twilio + LLM integration (D3) |
| 4 | Google Calendar OAuth + write-back                              | ⛔ not yet (D4) |
| 5 | Stripe subscription with metered booking-fee usage records      | ⛔ not yet (D4) |
| 6 | RLS policies enforce tenant isolation                           | 🟡 SQL written in `supabase/rls-policies.sql`; not yet applied to a live DB |
| 7 | Daily digest email rendered and delivered                       | ⛔ not yet (D4) |
| 8 | Operator dashboard (Next.js)                                    | ⛔ not yet (D4) |
| 9 | Two-party consent recording disclosure on every voice agent open | 🟡 prompt template in `src/ringback/prompts.py`; needs live verification on a real call |
| 10| Emergency keyword routing test                                  | 🟡 unit test in `tests/test_emergency.py`; not yet run against real Twilio |
| 11| `.env.example` documents every secret                           | ✅ present at repo root |
| 12| No PII in logs                                                  | ✅ `src/ringback/logging.py` redacts phone/email/name/address |
| 13| Idempotency on `create_booking` by (tenant, phone, slot)        | ✅ unit-tested |
| 14| Webhook replay protection                                       | 🟡 scaffolded; depends on production deployment to validate |
| 15| Health check + uptime probe                                     | ⛔ not yet |

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
- `pytest` runs the unit tests under `tests/` and they pass against the
  scaffold modules. (See "How to verify" below.)
- `.env.example` covers every secret referenced in code.
- No secrets committed (verified by `git diff` review).

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
