# T65 / Birthday Workflow

Turning-65 leads come in year-round and convert at significantly higher rates than AEP cold leads — they're approaching their Initial Enrollment Period (IEP) and most haven't decided yet. The cadence is timed to the IEP, not to a marketing calendar.

## IEP timeline (the 7-month window)

```
   ─3 months ──── birthday month ──── +3 months ─►
       │                │                  │
       │                │                  └──> IEP closes; lock-in penalties begin
       │                └──> Coverage can start this month
       └──> Earliest enrollment window opens
```

## Lead intake (any time before age 65 + 6 mo)

The T65 landing page (`t65-funnel.html`) collects birth month + birth year so we know:

- IEP open date = first day of (birth_month - 3) of birth_year + 65
- IEP close date = last day of (birth_month + 3) of birth_year + 65
- AEP-equivalent: any change can be made during AEP after first enrollment

A nightly cron (extension of workflow 11) computes IEP windows and sets per-lead "next outreach" dates.

## Pre-IEP (more than 3 months before birth month)

| Trigger | Channel | Content |
|---|---|---|
| Form submission | Email | `t65_welcome_v1` — primer on Medicare basics |
| 6 months before 65th birthday | Email | `t65_6mo_v1` — "What to do 6 months out" |
| 5 months before | Email | `t65_5mo_v1` — Part A vs Part B explained |
| 4 months before | Email | `t65_4mo_v1` — Original vs Advantage vs Supplement |

**No outbound calls in this window** unless the lead explicitly requests one.

## IEP open (3 months before through birthday month + 3)

| Trigger | Channel | Content |
|---|---|---|
| Day IEP opens | Outbound dial | "Your IEP opened today — happy to do that walkthrough now or any time in the next 7 months." |
| Day IEP opens + 0 | SMS | "Hi {first_name}, your Medicare Initial Enrollment Period opens today. Want to schedule a 15-min walkthrough? {scheduling_link}. STOP to opt out." |
| Day IEP opens + 0 | Email | `t65_iep_open_v1` |
| Day IEP opens + 14 (no booking) | Outbound dial | Same script |
| Day IEP opens + 30 (no booking) | Email | `t65_iep_30d_v1` |
| 30 days before birth_month | SMS | "Your birthday's in {N} days — and so is the most important coverage start date for your IEP. Want to make sure you're set? {scheduling_link}." |
| Birthday month start | Email | `t65_birthday_month_v1` — "Coverage can start this month" |
| 30 days before IEP close | Outbound dial | Final scheduled outreach |

## Birthday-day greeting (no sales pitch)

> "Happy birthday, {first_name}! No agenda on this one — just wanted to wish you a great day. If you ever want to chat about Medicare options, you know where to find me. Take care."

This call is **not** a Medicare marketing call (no recording requirement on a non-marketing greeting), but in practice: keep the disclaimer in the voicemail anyway, just to be safe.

## Special enrollment situations T65 leads commonly hit

- **Still working at 65 with employer health insurance.** Don't auto-pitch enrollment. Walk them through whether to delay Part B (avoid the late-enrollment penalty) and how the SEP works when they retire.
- **VA coverage.** Many veterans don't realize Medicare and VA work together. No plan pitch — refer to the VA explanation and offer a real human conversation.
- **Already on Marketplace insurance turning 65.** Coordinate transition; SEP-aware.
- **Helping a parent.** Treat the helper as the lead (their consent), but the parent is the prospective member. No PHI shared with helper without authorization.

## Post-IEP

If the T65 lead doesn't enroll during their IEP:

- Move to nurture for 1 year.
- Re-engage at the next AEP.
- Flag any pattern of T65 leads not enrolling for source-quality investigation.

## Compliance specifics for T65

- Birth month and year are PII. Capture only when needed; never display full DOB in any outbound message.
- Do not imply that not enrolling is a "loss" or "penalty trap" — the late-enrollment penalty is real but framing it as urgency in marketing is what triggers MCMG findings. Mention the penalty factually if the lead asks.
- No "free Part B" pitches — Part B is a federal program with a federal premium; agents have no role in pricing it.
