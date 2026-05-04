# Appointment Setting

The first call is to **set the appointment**, not to enroll. Holding that line is the single biggest predictor of compliance and close-rate health.

## When to ask for the appointment

After you've:

1. Identified yourself + said the disclaimer
2. Asked permission to continue
3. Asked 3–5 discovery questions
4. Heard at least one specific reason they want help (a worry, a change, a question)

Earlier than that and the lead doesn't have skin in the game; later and you've burned the call.

## The transition language

> "Based on what you've shared — {paraphrase of their issue} — I think it's worth us doing a 30-minute review where I can actually look at your specific situation. I won't recommend anything until we sign a Scope of Appointment form first — that's just a CMS requirement that says we agreed to talk about specific products. Sound okay?"

## The slot offer (always two-choice close)

> "I have **{day1 morning slot}** or **{day2 afternoon slot}**. Which is easier?"

Never ask "what works for you?" — that produces decision fatigue. Two choices, always.

## SOA email send

The booking workflow sends `appt_confirmation_v1` with the SOA link. Confirm verbally:

> "I'll send a quick email and text right now with the calendar invite and the Scope of Appointment link. Two-minute form. If you can fill it out before our call, we'll have a more productive conversation."

## Reminder cadence

| Time before | Channel | Content |
|---|---|---|
| 24 h | Email | Reminder + SOA link if not yet signed |
| 4 h | SMS | "Looking forward to talking at {time}. Reply STOP to opt out." |
| 30 min | SMS | "Calling at {time}. Make sure you're somewhere quiet." |
| At appointment | Outbound dial | Auto-fired by workflow 06 |

## SOA before plan-specific talk

Hard rule: **no plan-specific conversation until SOA is signed for the relevant product types.** If the lead hasn't signed:

> "Quick pause — I see we don't have your Scope of Appointment yet. Want to do that real quick over the phone? I'll read the products we're covering today and you say yes or no. (Read product list → wait for clear yes per product → confirm full name → record verbal consent.)"

Verbal SOA is allowed under CMS rules with documented evidence. Workflow saves an `soa_records` row with `signature_method='verbal'`, `signature_evidence_url` pointing to the recording.

## Closing the appointment

> "Great — confirmed for **{time on day}**. I'll call you at this number. Quick reminder: I'll restate the disclaimer that we're not Medicare and that the call is recorded. Anything else you want me to bring to that call?"

## What to never do at appointment-setting

- Don't quote a specific plan or carrier yet.
- Don't promise savings, "free benefits," or specific premiums.
- Don't forward to another agent or "specialist" without explicit reassignment in the CRM and full re-disclosure.
- Don't pretend the SOA is just a formality. It's the document that makes the next conversation legal.
