# Validation Plan — Ringback (Days 1–7)

Owner: Validation Agent. Reviewed by Growth, Sales, and Analytics Agents.

The point of this plan is **not** to build the product. It is to test
whether the offer described in `company-factory.md` is *wanted enough*
that strangers will book a 20-minute call about it within 7 days.

If the demand isn't there, we kill or pivot **before** writing more code.

---

## 1. Hypothesis

> If we email or DM owner-operators of HVAC, plumbing, electrical, and
> roofing companies in 5 Sun-Belt metros, with a one-line offer to recover
> their missed jobs for $249/mo + $25/booked-job, **at least 8 out of 150**
> will book a 20-minute discovery call within 7 days.

Why 8/150: that's a 5.3% positive-reply rate, which historically separates
"there is a real wedge" from "you're spamming."

## 2. Go / No-Go Gates

| Metric                                     | Go     | Watch       | Kill / Pivot |
|--------------------------------------------|--------|-------------|--------------|
| Booked discovery calls / 150 messages      | ≥ 8    | 4–7         | < 4          |
| Show-up rate on booked calls               | ≥ 60%  | 40–59%      | < 40%        |
| "Yes, I'd pay $249 today" on the call      | ≥ 30%  | 15–29%      | < 15%        |
| Pilot deposits / payment intents           | ≥ 3    | 1–2         | 0            |

If 3+ pilots prepay (or sign month-to-month), proceed to MVP build.
Below the watch zone: stop and re-evaluate the offer before any more code.

## 3. Channels and Volumes

| Channel                            | Volume / wk | Audience                                  |
|------------------------------------|-------------|-------------------------------------------|
| Cold email (manual, reviewed)      | 100         | Owner emails from public license boards   |
| LinkedIn DM                        | 30          | Owners with LinkedIn presence             |
| Trade Facebook group value posts   | 5 posts     | r/HVAC, "HVAC Owners Helping Owners," etc.|
| Direct text **only on opt-in**     | as opted-in | After Facebook DM consent                 |

We do **not** purchase lead lists. We do **not** scrape any site whose
ToS prohibits it. We do **not** SMS unsolicited.

## 4. Cold Email Script (variant A — pain-led)

Subject: missed calls = lost jobs?

Body:
```
Hey {first_name} — I run a small team that helps {trade} shops in
{metro} stop losing jobs to missed calls. Our AI answers when your crew
can't, qualifies the customer, and books straight into your calendar.

Most shops we talk to are missing 30–50% of their inbound — that's a
real number when the average ticket is what it is.

$249/mo + $25 per booked job. No contracts. Setup is same-day.

Worth 15 minutes this week to see if it'd pay for itself?

— {founder_first_name}
{founder_phone}

P.S. Happy to send a 90-second demo of an AI agent answering a real
HVAC call — just reply "demo."
```

## 5. Cold Email Script (variant B — curiosity-led)

Subject: a question about your after-hours line

Body:
```
{first_name} — quick question. When a customer calls your shop on a
Saturday at 4pm and nobody picks up, where does that call go?

I ask because we built a thing that handles those calls (voice + text)
and books the job into your calendar before the customer calls the next
{trade} on the list. Pricing is built around success — $249/mo +
$25 per booked job.

Worth 15 minutes? I'll show you a recorded call from a real shop.

— {founder_first_name}
```

We split-test 50/50. Winner becomes the default.

## 6. LinkedIn DM (short)

```
{first_name} — building an AI receptionist priced for {trade} shops
($249/mo + $25/booked-job, no contracts). Most owners we talk to are
losing 30–50% of inbound calls.

Worth 15 min to see a real demo?
```

## 7. Discovery Call Script (20 min)

1. **Rapport (2 min)** — "Where are you headed today, where you been, what's the truck count?"
2. **Pain mining (8 min)** — open questions:
   - "Walk me through what happens when a customer calls and nobody picks up."
   - "What's the avg ticket on a service call vs. an install?"
   - "Last time you found out you'd missed a job — how'd you find out?"
   - "What've you tried to fix it — receptionist, answering service, text-back?"
3. **Story-led demo (5 min)** — play a 90-second Twilio + LLM recording of an
   AI agent qualifying an HVAC call. (Pre-recorded; this is validation, not product.)
4. **Offer (3 min)** — "$249/mo + $25 per booked job, no contracts.
   We onboard you in a day. First 14 days free, no card needed."
5. **Close / next step (2 min)** — "If we built this for you starting Monday,
   do you want in?" If yes: send Stripe payment-link for $1 deposit
   (refundable, just to filter tire-kickers) and book the onboarding call.

## 8. Landing Page Hypothesis

URL: `ringback.ai` (placeholder; reserve in a later step if metrics pass).
Above the fold:
- **Headline:** "Stop losing jobs to missed calls."
- **Subhead:** "Ringback answers, qualifies, and books — voice and text — for HVAC, plumbing, and roofing shops. $249/mo + $25 per booked job."
- **Primary CTA:** "Hear a real recovered call →" (opens audio sample).
- **Secondary CTA:** "Book a 15-minute demo."
- **Social proof slot:** TBD after first 3 pilots.

Tracking: Plausible (no cookies needed). Goal events:
`view`, `play_demo_audio`, `clicked_book_demo`, `submitted_form`.

## 9. Survey Questions (sent if no reply after 5 days)

```
1. On a scale of 1–10, how painful are missed calls for your shop right now?
2. What's your average service-call ticket?
3. What have you already tried to fix the missed-call problem?
4. If a service answered + booked your missed calls for $249/mo + $25 per
   booked job, would you try it for 14 days free? (yes / maybe / no)
```

## 10. What we will NOT do during validation

- Build the full MVP. (We have a *demo recording*, not a product.)
- Onboard a paying customer to a half-built system. If validation proves
  out, we *then* spend D2–D6 building.
- Buy ads. Cold outbound is the test bed.
- Promise integrations we haven't built. We can promise Zapier; we cannot
  promise ServiceTitan-direct yet.

## 11. Outputs the Validation Agent must produce by D7

- 150 sent messages logged with timestamp, channel, variant, response.
- Reply spreadsheet with sentiment + objection tagged.
- ≥ 8 booked discovery calls (or document the kill / pivot trigger).
- 3 recorded discovery calls + transcripts.
- Top 5 objections with proposed responses → handed to Sales Agent.
- Final go/no-go memo to CEO-Orchestrator.
