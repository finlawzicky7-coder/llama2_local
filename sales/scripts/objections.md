# Objection Handling

Rules for every objection response:

1. **Acknowledge first.** Reflect back what they said before you respond.
2. **Stay neutral.** Never make a savings claim, plan claim, or government implication.
3. **One sentence answer, one question back.** Don't monologue.
4. **Honor any opt-out.** If the objection includes "stop calling" or equivalent, set opt-out and end politely.

---

## "I'm not interested."

> "Totally understood — I won't keep calling. Just so I close your file accurately, is it that the timing's off, or that you're already happy with your current coverage?"

If "happy with current coverage": *"Glad to hear it. I'll close the file. If your plan ever changes its drug list or your doctors leave the network, you can always reach back out."* → end, mark `not_interested`.

If "timing's off": *"Got it. Want me to circle back closer to AEP in October?"* → schedule callback.

---

## "Are you Medicare?"

> "No — and that's an important question. I'm a licensed insurance agent at {AGENCY_NAME}, an independent agency. We're not Medicare and not affiliated with the government. You can always reach Medicare directly at 1-800-MEDICARE or Medicare.gov. Want me to keep going, or would you rather start there first?"

---

## "How did you get my number?"

> "You filled out a request for a Medicare review on **{landing_page}** at **{timestamp}**. I have a record of it. If that wasn't you, I'll mark you as opted-out right now and you won't hear from us again."

---

## "Just send me information by email."

> "Happy to. I'll send a plain-English Medicare basics guide that doesn't recommend any specific plan. The plan-specific details we'd cover on a call after you sign the Scope of Appointment form. Cool?"

---

## "I already have an agent."

> "That's great — they probably already do a great job for you. Quick check: when did they last review your plan with you? Plans change every year, so a fresh look from a different perspective sometimes catches things. No pressure either way."

---

## "What's the catch?"

> "Fair question. Here's how I get paid: when someone enrolls through me, the carrier pays me a commission set by Medicare itself — same amount whether you pick Plan A or Plan B. So I have no incentive to push one plan over another. The Scope of Appointment form locks that in."

---

## "Is this free?"

> "There's no charge to talk to me, ever. Plans have their own premiums set by the carriers — those costs are the carrier's, not mine. We don't charge you anything."

(Do **not** say "this is a free service" or "this is free" — frame as "no charge to talk to me.")

---

## "Can you save me money?"

> "I genuinely don't know yet — and I'm not allowed to promise savings. What I can do is take an honest look at your current premium, your doctors, and your prescriptions, and tell you whether what's available where you live could be a better fit. Sometimes it is, sometimes the plan you're on already is the right one."

---

## "I need to think about it."

> "Of course. Two options: (1) I send you the Medicare basics guide and you read it on your time, or (2) we tentatively grab a 15-minute slot for next week and you can cancel any time. Which is easier?"

---

## "Don't ever call me again."

> "Absolutely. I'm marking you as opted out across all channels right now — phone, text, and email. If you ever change your mind you can text START. Take care."

→ Flag `outcome=opt_out`. The dialer screen has a hardcoded button that calls `fn_propagate_opt_out`. **Never** require the lead to repeat themselves.

---

## "Are you recording this?"

> "Yes — every Medicare-related call is recorded, that's a CMS requirement, and you consented to that on the form. If you'd rather not continue, I completely understand — I can end the call now."

---

## "Why do you need my zip code?"

> "Plans are licensed by zip — what's available where you live is different from what's available a county over. I don't need your full address, just the zip."

---

## "I don't trust this."

> "Totally fair — there are bad actors in this space and I appreciate the skepticism. Two things I can do: (1) I'll send my license number and the agency's NPN by email so you can verify; (2) you can also call us back at our published number, **{PHONE}**, and ask for me by name. Want me to do that?"
