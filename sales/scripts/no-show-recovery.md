# No-show Recovery

Most missed appointments are **logistics**, not rejection. The recovery sequence assumes good faith, makes one polite follow-up, and exits cleanly if there's no response.

## Minute 0 (appointment time): outbound dial

If the dialer (workflow 06) gets no answer at the scheduled time:

- Wait 5 minutes; auto-redial once.
- If still no answer: drop voicemail (V2 from `voicemail.md`).

## Minute 5: SMS

> {AGENCY_NAME}: Hi {first_name}, this is {agent_first_name}. I just tried you for our scheduled Medicare review at {time}. Want to try again now? Reply YES or pick a new time: {scheduling_link}. Reply STOP to opt out.

## Minute 30: email

**Subject:** Missed you at {time} — easy to reschedule

> Hi {first_name},
>
> I tried calling at {time} for the Medicare review you scheduled — totally fine, life happens. Pick any time that works: {scheduling_link}.
>
> Or reply with a window and I'll find something that fits.
>
> Riley · Licensed Agent · {AGENCY_NAME}

## Day 1: SMS reschedule attempt

> {AGENCY_NAME}: {first_name}, no pressure — just want to give you another chance to do that 15-min Medicare review. {scheduling_link}. STOP to opt out.

## Day 3: voicemail (V2)

## Day 7: graceful exit email

**Subject:** Closing your file — open invitation

> Hi {first_name},
>
> I'll close your file for now since we couldn't connect. The door's open if you ever want to circle back: {scheduling_link}.
>
> All the best — Riley

## After day 7: nurture only

Move the lead to `bucket='nurture'`. Monthly evergreen email (`monthly_evergreen` template). No more outbound dials. No more SMS. Email opt-out is one-click anywhere in the journey.

## CRM updates on no-show

- `appointments.status = 'no_show'` — set automatically by the dialer outcome handler.
- `leads.status = 'no_show'` until the recovery cadence ends.
- `compliance_audit_events`: log a single `event_type='no_show_recovery_started'` event for traceability.
- The agent does **not** mark the appointment "completed" — completion happens only on actual conversation.

## What never happens on a no-show

- The agent does not place more than 3 dials on the no-show day.
- The agent does not call before 8am or after 9pm lead-local, even on the same day.
- No "shame" or "loss" framing in messages ("you wasted my time," "you missed your chance").
- No prediction of plan loss, deadline pressure, or savings forfeit.
