# First Call Script

> Read the bracketed parts verbatim. Everything else is conversational. The TPMO playback IVR has already played before you bridged — but you must still say the short disclaimer in your own words within the first 60 seconds and then re-anchor compliance throughout.

---

## Phase 1 — Greet and identify (≤ 30 seconds)

> "Hi, is this **{first_name}**? Great. This is **{agent_first_name}** with **{AGENCY_NAME}** — I'm a licensed insurance agent calling about the Medicare review you requested at **{landing_page}** earlier today/this week."

If they're confused: *"You filled out a quick form looking for help understanding your Medicare options — does that ring a bell?"*

If still confused: *"No problem. I'll send you an email so you have my info, and I won't keep calling. Have a great day."* → end, mark `outcome=wrong_number` if it really wasn't them.

---

## Phase 2 — TPMO compliance anchor (within first 60 seconds)

> "Just to be clear before we go any further — I'm not Medicare or the federal government, and we're not Medicare.gov. **{AGENCY_NAME}** is an independent agency. We don't offer every plan available in your area. We currently represent {N_CARRIERS} organizations offering {N_PLANS} products in your area, and you can always go to Medicare.gov, call 1-800-MEDICARE, or contact your local SHIP for all your options."

> "And this call is being recorded for quality and compliance. Are you good with that?"

If yes: continue.
If no: *"Totally understand — I'll have to end the call since we're required to record. I can email you instead — would that work?"*

---

## Phase 3 — Permission and frame (≤ 60 seconds)

> "I have about ten minutes if you do — and the goal isn't to sell you anything today. It's to ask a few questions, understand your situation, and see whether it makes sense to schedule a longer **Medicare review** with me. Sound fair?"

If yes: continue.
If "I only have a couple minutes": *"Got it — I'll keep it tight."*
If "I'm busy": *"Totally fair. When's a better time today or tomorrow — morning or afternoon?"* → set callback, capture in CRM.

---

## Phase 4 — Discovery (open, no plan-specific questions)

Ask only what you need. Do **not** mention specific carriers, plans, or benefits.

> 1. "Are you on Medicare today, turning 65 soon, or helping someone else?"
> 2. (If on Medicare) "How long have you been on Medicare?"
> 3. (If on Medicare) "Are you currently on Original Medicare, on a Medicare Advantage plan, or do you have a Medicare Supplement plus a separate drug plan? — and don't worry if you're not sure."
> 4. "Are there one or two **specific things** you wanted help with — for example, your prescriptions, your doctors, your monthly costs, or just getting a clearer picture?"
> 5. "And this is the best phone and email to reach you on?"

---

## Phase 5 — Set the appointment (the only real ask of this call)

> "Based on what you've shared, the right next step is a 30-minute Medicare review where I can look at your current coverage, your doctors, your prescriptions, and the options available where you live. **I'm not going to recommend anything until we sign a Scope of Appointment** — that's just a CMS form that says we agreed to talk about specific products. Cool?"

> "I have **{slot 1}** or **{slot 2}** open this week — which is easier?"

Once a slot is chosen:

> "Perfect. I'll send a calendar invite and a link to sign the Scope of Appointment ahead of time. **A quick reminder**: when we talk on **{day}**, I'll re-state that I'm not Medicare, I represent multiple carriers, and the call will be recorded — same as today. Sound good?"

---

## Phase 6 — Close out (≤ 30 seconds)

> "Last thing — if you change your mind anytime, just text **STOP** to any message we send and we'll stop contact across phone, text, and email. Thanks for your time today, **{first_name}** — talk soon."

---

## Things to never say on a Medicare call

- "I can save you money" / "guaranteed savings"
- "This is the best plan"
- "Free benefits" / "free money"
- "Everyone qualifies for this"
- "I'm with Medicare" / "I work with the government"
- "You're going to lose your coverage if you don't act today"
- The specific name of any carrier or plan **before SOA is signed**
- "Just give me your social and we'll get you signed up right now"

## After the call

- Write `call_logs.outcome` (the dialer screen lets you pick).
- Add a 1-line summary in `call_logs.notes` (the AI summarization will run too).
- If they opted out, ensure the dialer screen flips opt-out — the workflow 09 listener also catches inbound STOP texts; agent-flagged opt-outs hit the same flow via `fn_propagate_opt_out`.
- If you set an appointment, confirm the SOA email arrived in the lead's inbox.
