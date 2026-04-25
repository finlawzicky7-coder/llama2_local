# Operations SOPs — Ringback

Owner: Operations Agent. Reviewed by QA, Engineering, Sales, and Legal Agents.

These SOPs cover everything that has to happen *after* a tenant signs the
trial. They are designed so a single non-technical operator can run the
fulfillment side of the business with checklists alone.

---

## SOP-1 — Tenant Onboarding (target: ≤ 24 hours)

**Trigger:** Sales Closer hands off in `#new-tenants` Slack channel.

**Steps:**

1. **Create tenant in app** (admin panel → Create Tenant).
2. **Invite owner** by email; verify they accept and set password.
3. **Provision Twilio number** in their preferred area code.
   - If toll-free needed: confirm 10DLC/toll-free verification kicked off.
4. **Configure tenant**: hours, ZIPs, job types, avg tickets, emergency
   keywords, on-call number, language (English / English+Spanish flag).
5. **Connect Google Calendar** (OAuth) — owner must complete this step.
6. **Walk through call forwarding** on a recorded screenshare:
   - AT&T: `*61*+1XXXXXXXXXX#`
   - Verizon: `*71XXXXXXXXXX`
   - T-Mobile: `**61*+1XXXXXXXXXX#`
   - VoIP (RingCentral, Grasshopper): per-vendor instructions in tenant doc.
7. **Place 3 test calls** through the forwarded line:
   - Test 1: standard service request → must produce booking + GCal event.
   - Test 2: emergency keyword ("flooding," "no heat in winter," "fire") →
     must route to on-call number.
   - Test 3: SMS-first inbound → must produce booking.
8. **Send welcome email** with: dashboard URL, demo recording, owner
   pocket-card with the AI's persona name.
9. **Mark tenant `live`** in admin; tenant now appears in daily digest.

**Time SLA:** 24 hours from sales hand-off to `live`. If exceeded,
auto-escalate to founder.

## SOP-2 — Daily Operations Standup (15 min, async)

**When:** 9am tenant-region (US Central by default).

**Inputs:**
- Yesterday's digest report (calls, bookings, missed/lost).
- Open support tickets.
- Twilio cost report (alerts if any tenant > 2x baseline).
- LLM cost report (alerts if any tenant > 2x baseline).

**Outputs:**
- Per-tenant flag if booking rate dropped > 30% week-over-week.
- Per-tenant flag if a single call > $1.50 cost (almost always = a hung call).
- Action items into `ops-board`.

## SOP-3 — Customer Support

**Channels:** email (`help@ringback.ai`) and in-app chat.

**SLA:**
- Free trial: 1 business day.
- Paid: 4 business hours, 9am–9pm CT.
- Emergency (calls not flowing through, billing dispute): 1 hour, 24/7.

**Common issues + scripts:**

1. **"My calls aren't reaching the AI."**
   - Verify Twilio number is active.
   - Verify forwarding is configured at the carrier (have them dial
     `*#21#` on iPhone / Android to inspect).
   - Place a test call from an unrelated phone.
   - Check `events` log for any inbound webhook in last 24h.
2. **"My customer said the AI was confusing."**
   - Pull the transcript.
   - If AI failed: file a regression ticket with transcript + audio.
   - If buyer-side confusion: offer to tweak greeting copy.
3. **"I got billed for a job that didn't book."**
   - Pull the booking + GCal event.
   - If booking truly didn't materialize, refund the $25 immediately
     via Stripe and credit a future booking.
4. **"Can you do outbound for me?"**
   - Polite no. Reaffirm the inbound-only policy.

## SOP-4 — Refund / Cancellation

- Trial cancel: self-serve in app; no questions asked.
- Paid cancel within month 1: full refund of subscription. Booking fees
  retained because the bookings happened.
- Paid cancel after month 1: pro-rate; or finish out month.
- Always send: a 5-question exit survey, a real human note, and a
  one-question NPS. Log all answers in `agent-memory.md` lessons file.

## SOP-5 — Incident Response

**P0 — calls not flowing for any tenant.**
- Pager → founder + on-call engineer.
- Public status page updated within 15 min.
- Post-mortem within 72 hours.

**P1 — billing or PII issue affecting one tenant.**
- Direct call to owner within 1 hour of detection.
- Written summary within 24 hours.

**P2 — AI quality regression on a single tenant.**
- Pull transcripts; revert prompt or model version if needed; notify tenant.

## SOP-6 — Compliance Maintenance

Quarterly:
- Review 10DLC campaign registration; renew if needed.
- Re-test two-party-consent recording disclosure on all voice scripts.
- Review terms / privacy policy version against latest state additions.
- Re-confirm Twilio attestation status.

Annually:
- DPA template review.
- Insurance review (E&O + cyber).
- Vendor risk review (Twilio, Stripe, Supabase, LLM provider, ElevenLabs).

## SOP-7 — Internal Dashboards (spec)

The Operations Agent owns four dashboards (built on Supabase data):

1. **Live Operations** — calls in progress, latency, error rate.
2. **Tenant Health** — per-tenant 7-day booking rate, missed-call rate,
   churn risk score.
3. **Unit Economics** — cost per call, cost per booking, gross margin
   per tenant.
4. **Pipeline** — discovery calls, trials, paid, churned (sales mirror).

## SOP-8 — Knowledge Loop

Every escalation, every refund, every tenant call recording must be
referenced in the weekly Friday review. Patterns get promoted into
prompts (Automation Agent), product changes (Engineering Agent), or
script changes (Sales Agent). The Memory & Documentation Agent
maintains the canonical lessons file in `agent-memory.md`.
