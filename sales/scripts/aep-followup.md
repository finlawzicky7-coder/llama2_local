# AEP Follow-up Workflow (Oct 15 – Dec 7)

The Annual Enrollment Period concentrates 60–70% of the year's enrollment volume into 7 weeks. The follow-up cadence here is denser than evergreen, but the rules are the same: TPMO disclaimer, no plan/savings claims, no pressure language.

## Pre-AEP warm-up (Sep 15 – Oct 14)

Goal: re-establish contact before the rush so AEP isn't a cold start.

| Day | Channel | Template / Script |
|---|---|---|
| Sep 15 | Email | `monthly_evergreen` (October version: "What changes in Medicare this fall") |
| Sep 22 | SMS to existing clients only | "Hi {first_name}, this is {agent_first_name} — a heads-up your Annual Notice of Change letter is coming this month. Want a quick review when it arrives? Reply YES or STOP." |
| Sep 30 | Email | "Your ANOC checklist" — plan-neutral guide on what to look for |
| Oct 12 | SMS to existing clients | "AEP starts Oct 15. Reply REVIEW to schedule a 15-minute look at your plan, or STOP to opt out." |

## During AEP (Oct 15 – Dec 7)

### New leads (HOT/WARM)

Run the standard cadence from `sms-cadence.md` and `email-cadence.md`, but with these compressions:

| Step | Standard | AEP |
|---|---|---|
| First dial | ≤ 60 s | ≤ 60 s (unchanged) |
| Second dial (if no contact) | 4 h | 2 h |
| Day-1 SMS | morning | morning + late afternoon |
| Voicemail | once per day | once per day (no change) |
| Email cadence | 1 / 4 / 7 / 14 | 1 / 3 / 7 / 14 |

### Existing clients

Personal outreach from their assigned agent only — never auto-dial existing clients during AEP without confirming consent freshness.

> "Hi {first_name}, it's {agent_first_name}. AEP is open and I wanted to reach out for our annual review. The plan you're on may have changed for next year. Want to grab 15 minutes this week or next?"

## Hard rules during AEP

1. The TPMO disclaimer applies at full force, every call, every appointment, every email, every SMS template. AEP does **not** relax disclosure.
2. No "limited time" or "deadline" pressure messaging in templates. The deadline (Dec 7) is real, but framing it as urgency in marketing is what gets agencies into MCMG trouble. Mention the date neutrally; do not require action "today."
3. Agents must re-verify every plan recommendation against current-year formulary, network, and benefits using the carrier's tools — never from memory.
4. Every enrollment must follow CMS pre-enrollment checklist, plan disclosure, and have a fresh SOA signed at least 48 hours prior **unless the lead reached out unsolicited** (the SAOA exception). Document which path each enrollment took.
5. Door-to-door, unsolicited outbound calls to non-customers, and unsolicited approaches at health fairs are off-limits per CMS rules.

## AEP playbook for the team

- **Daily 8:30 standup.** Quick check: queue depth, agents at capacity, exceptions overnight, today's appointment count.
- **Compliance stand-down at any critical exception.** A `tpmo_missing` or `unlicensed_outreach` from the daily audit halts that agent's outbound until reviewed.
- **Live monitoring.** Compliance officer listens to one randomly-sampled call per agent per day; coaching note posted same day.
- **Recording review threshold.** If summarization detects any of: `named_specific_plan` before SOA, `made_savings_guarantee`, `claimed_government_affiliation`, `ignored_opt_out` — auto-page to compliance.
- **Daily KPI digest** (workflow 11) goes to leadership at 18:00 with: enrollments by carrier/state/agent, application-submission errors, post-call compliance flags.

## Post-AEP (Dec 8 – Jan 31)

- Pause outbound dialing of cold leads for 48 h to clean up exceptions.
- Run a full compliance audit (extended workflow 10) and snapshot all consent versions for archive.
- Move all leads not enrolled by Dec 7 to nurture; revisit at OEP (Jan 1 – Mar 31) only for those eligible.
