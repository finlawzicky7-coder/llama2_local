# SMS Cadence

All SMS templates carry: agency identifier, opt-out instruction, no plan/benefit/savings claims, no government implication.

## Step 1 — Concurrent with first-attempt dial (HOT)

> {AGENCY_NAME}: Hi {first_name}, this is {agent_first_name}, your licensed agent. Tried calling about your Medicare review request. Reply CALL to schedule, or reply STOP to opt out. Msg & data rates may apply. Not Medicare / not the federal government.

## Step 2 — 4 hours after first attempt, no contact

> Hi {first_name} — still happy to do that 15-min Medicare review when convenient. Pick a time: {scheduling_link}. Reply STOP to opt out.

## Step 3 — Day 1 morning

> Good morning {first_name}. Easiest day for a quick Medicare review — today, tomorrow, or later this week? Reply with a day, or STOP to opt out.

## Step 4 — Day 3

> {first_name}, no pressure — we're just here when you're ready. Reply CALL or pick a time: {scheduling_link}. STOP to opt out.

## Step 5 — Day 7

> {first_name}, friendly check-in — I can also send a 1-page Medicare basics guide instead of a call. Reply GUIDE for the email or CALL to talk. STOP to opt out.

## Step 6 — Day 14 (final)

> {first_name}, this is my last note. I'll close out your file unless I hear back. Reply CALL to talk or STOP to opt out. Thanks!

---

## Reply handling

- **STOP / UNSUBSCRIBE / END / CANCEL / DO NOT CALL / REMOVE** → workflow 09 immediately processes opt-out and replies with the standard ack: *"You have been unsubscribed and will no longer receive messages from us. Reply START to resubscribe."*
- **CALL** → workflow 07 cadence triggers an immediate dial attempt (compliance-gated).
- **YES / SCHEDULE / BOOK** → reply with `scheduling_link`.
- **GUIDE** → reply with the educational PDF link (an approved, plan-neutral guide).
- **HELP** → standard 10DLC help reply: *"{AGENCY_NAME}: Reply STOP to opt out. Msg & data rates may apply. Contact: {PHONE}."*

## Compliance constraints

- **10DLC** registered and **brand verified**. Use the approved campaign for "insurance lead capture & sales."
- Never include a plan/carrier name in a templated SMS — only in 1:1 messages after SOA.
- Send only between 08:00 and 21:00 lead-local.
- Cap at 1 SMS per lead per day in cadence; 2/day max if the lead is replying.
- All templated bodies stored in version control; changes require compliance review.
