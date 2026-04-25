# Sales Playbook — Ringback

Owner: Sales Closer Agent. Reviewed by Growth, Operations, and Legal Agents.

For the founder + first hire. No SDR layer at this stage.

---

## 1. Lead Lifecycle

```
Outbound → Reply / Inbound → Qualification SMS → Discovery call (20 min)
       → Free trial (14 days) → Paid (Stripe) → Onboarded → First booking
       → Case study candidate → Expansion (Tier 2) / Referral
```

## 2. Qualification Criteria (BANT-ish, contractor-tuned)

A "good fit" lead is:

- U.S. home-services contractor in: HVAC, plumbing, roofing, electrical,
  garage door, locksmith, appliance repair, pest control.
- 1–25 trucks (sweet spot: 3–10).
- Owner-operator OR office manager with explicit owner buy-in for $249–$799/mo.
- Already missing inbound calls today (self-reported on call).
- Has at least one of: Google Calendar, Jobber, Housecall Pro, ServiceTitan,
  Workiz, FieldEdge.
- Comfortable forwarding their existing line on busy/no-answer (we walk them
  through it on the call).

Disqualifiers (politely close):
- Solo operator with truly < 5 calls/week (ROI doesn't math).
- Wants outbound cold-calling. (Not our product.)
- Refuses month-to-month and demands annual contract day one. (Pricing
  isn't ready for that yet.)
- Already locked into a Numa/Goodcall annual.

## 3. Lead Scoring

| Signal                                       | Points |
|----------------------------------------------|--------|
| 3–10 trucks                                  | +20    |
| HVAC/plumbing/electrical                     | +15    |
| Sun-Belt metro                               | +10    |
| Owner is on the call                         | +20    |
| Self-reported >30% missed calls              | +20    |
| Avg ticket > $300                            | +10    |
| Already has a CRM (HCP/Jobber/ServiceTitan)  | +10    |
| Active Google Business Profile               | +5     |
| 1-truck shop                                 | -10    |
| Wants outbound dialing                       | -50    |
| Wants enterprise/multi-loc immediately       | -15    |

Score ≥ 60 → fast-track to demo. Score < 30 → polite close, move on.

## 4. Discovery Call Script (canonical)

See `validation-plan.md` §7 — same script during validation and post-launch.
Closer add-ons below:

### Pre-call (3 minutes before)
- Pull up: their Google Business Profile, last 5 reviews, any Yelp reviews
  mentioning "couldn't reach" / "no answer" / "voicemail." Use as natural
  proof in the call. Never fabricate.

### Opening
> "Appreciate you making time. I run a small team that builds the
> AI receptionist for HVAC and plumbing shops your size. Quick question
> before I pitch you anything — when a customer calls and nobody picks
> up, where does that call go today?"

### The pivot
After they describe the chaos:
> "Yeah, that lines up with what other {trade} shops in {metro} are
> seeing. Let me show you what a real recovered call sounds like."

→ Play 90-second demo recording. Watch their face. Shut up.

### The offer
> "It's $249 a month plus $25 per booked job. No contracts. We get you
> live in a day. First 14 days are free, you don't even put a card down.
> If we don't recover at least one job for you in the first month I'll
> personally refund the $249. The booking fees you only pay on jobs we
> actually put on your calendar — those are real money."

### The close
> "If we built this for you starting Monday, do you want in?"

Three possible answers:
- **Yes** → "Great. I'll text you a Stripe link for a $1 refundable
  deposit just to lock the spot, and a calendar invite for onboarding
  tomorrow morning."
- **Maybe** → "What's the one thing that'd make this an obvious yes?"
- **No** → "Totally fair. Can I ask what made it a no — was it timing,
  trust, or fit?"

Whatever the answer, log it.

## 5. Objection Bank

| Objection                                          | Response                                                                                              |
|----------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| "We use HCP/Jobber's missed-call text-back."       | "Right — that texts. We *answer*, qualify, *and* book. The text-back catches one in ten. We catch six in ten. Want to A/B against your current setup for 14 days free?" |
| "AI sounds robotic on the phone."                  | "Play the demo. If your customer hangs up on a robot, we eat the cost. The AI is good enough that 80% of callers don't know."                                       |
| "What if it screws up an emergency call?"          | "Emergency keywords route straight to your on-call number — we never put an emergency through the booking flow. We can show you the call tree."                     |
| "I don't want to switch numbers."                  | "You don't. You forward your existing line on busy/no-answer to our number. If you cancel, the forwarding goes away. Your number is yours."                         |
| "What does it cost me if you don't book anything?" | "$249. That's it. The $25 per-booking is success-based — no booking, no fee. And month one is refundable."                                                          |
| "I want to talk to my wife/partner first."         | "Totally — let's get them on a 10-minute call together this week. I'll send 3 times."                                                                              |
| "I had a bad experience with Numa."                | "Got you. Numa is enterprise-priced and enterprise-paced. We're built for shops your size. Can you tell me what specifically Numa got wrong, so I can show you whether we'd hit the same wall?" |
| "What about my data / customer privacy?"           | "Data is encrypted at rest, isolated per tenant via row-level security, and we never sell it. We can sign a basic DPA if you want it. Recordings are retained 90 days unless you ask otherwise." |
| "I want a 30-day trial, not 14."                   | "Tell you what — if at day 14 you've gotten zero recovered jobs, I'll personally extend you to 30 free. Deal?" (Documented exception; track conversion.)            |

## 6. Follow-Up Sequence

Day 0 (call): personal "thanks + recap" email + Stripe link.
Day 1: SMS check-in if not paid.
Day 3: text the demo audio + 1 short proof point.
Day 7: text "still want to grab a slot?" + alt times.
Day 14: "moving on for now — should I close your file or keep you posted on
new features?" (Polite close.)

All follow-up must respect the lead's reply-stop preferences.

## 7. Onboarding Hand-off (to Operations Agent)

Closer sends to ops checklist (see `operations-sop.md`):
- Tenant name, owner email + phone.
- Plan tier and Stripe customer id.
- Existing phone number(s) to forward.
- Hours of operation, time zone.
- Job-type list + avg ticket.
- Service ZIPs.
- Calendar of choice (GCal / HCP / Jobber).
- Emergency keywords + on-call number.

## 8. Pricing Discipline

- Standard: $249 / $499 / $799 + $25/booked-job.
- Discount authority for the founder: up to 20% off Tier 1 for the first
  10 logos to seed proof. Documented in Stripe metadata.
- No "free forever" plans. No barter. No one is on Ringback for free
  beyond the trial.

## 9. Hand-back Triggers

If during onboarding we discover the buyer is unfit (e.g., tries to wire
in outbound dialing, has an active complaint to the BBB about a refund
dispute, asks for off-platform integrations we cannot support), the
closer hands the account back to the founder for a polite cancellation
+ refund within 24 hours.
