# Compliance Officer Runbook

The day-to-day operating manual for the compliance officer. Pair this with `audit-procedures.md` (the policy) — this file is the schedule and the queries.

> **One non-negotiable principle:** if a critical exception fires, *outbound stops first, root-cause is investigated second*. Never the other way around.

---

## Daily — 09:00

### 1. Read overnight Slack digests

Two Slack messages should have arrived overnight:

- **#compliance-audit** — workflow 10's daily compliance audit (03:00).
- **#compliance-ai-review** — AI auditor's exception list (04:00).

If either is missing, ping engineering immediately — the cron is broken, not "no findings."

### 2. Triage critical exceptions

```sql
select created_at, event_type, severity, lead_id, agent_id, details
from compliance_audit_events
where created_at >= now() - interval '24 hours'
  and severity in ('error','critical')
order by severity desc, created_at desc;
```

For each row:

| Severity | Action |
|---|---|
| `critical` | Halt the affected agent's outbound (`update agents set active=false where id=...;`). Investigate within 1 hour. |
| `error` | Open ticket, investigate within 4 business hours. |
| `warn` | Aggregate weekly; review on Monday. |

### 3. Listen to a sample of recordings

```sql
select c.id, c.agent_id, a.full_name, c.duration_seconds, c.outcome, r.storage_path
from call_logs c
join agents a on a.id = c.agent_id
left join recordings r on r.call_log_id = c.id
where c.created_at >= current_date - 1
  and c.outcome in ('connected','appointment_set','sold')
order by random() limit 5;
```

For each: open a signed URL, listen to the first 90 seconds + the closing 60 seconds. Confirm:

- TPMO disclaimer in the first 60 s (auto-played by IVR but verify).
- Recording notice acknowledged.
- No prohibited claims (no carrier/plan name pre-SOA, no savings guarantee, no government implication).
- Closing properly captures opt-out preference.

If anything is off, log a coaching note in the agent's file and flag the call: `update call_logs set notes = coalesce(notes,'') || E'\n[CO REVIEW] ...' where id = '...';`

### 4. License expiration scan

```sql
select a.full_name, al.state, al.license_number, al.expires_at,
       al.expires_at - current_date as days_left
from agent_licenses al join agents a on a.id = al.agent_id
where al.active and a.active and al.expires_at <= current_date + interval '60 days'
order by al.expires_at asc;
```

- ≤ 60 days: notify agent, kick off renewal.
- ≤ 30 days: also notify ops; if no renewal in flight, suspend that agent's leads in that state via routing.
- Expired: hard-disable the license row (`update agent_licenses set active=false where id=...;`).

### 5. Update the daily compliance log

Maintain a single dated entry in `compliance/daily-log.md` (you create this file in your fork):

```
2026-05-04
- Critical events: 0
- Errors: 1 (recording_missing on call_log_id=xyz, root-caused to Twilio webhook retry — fixed)
- Recordings reviewed: 5
- Coaching notes filed: 1 (Riley — disclaimer at 1:14, push earlier)
- Licenses expiring ≤60d: Riley FL (2026-06-30), Jordan TX (2026-06-15)
- Sign-off: Compliance Officer Name
```

This is your audit trail. Do not skip days.

---

## Weekly — Monday 10:00

### 1. Trend review

```sql
-- Critical exception trend (last 28 days, daily)
select date_trunc('day', created_at)::date as d, count(*)
from compliance_audit_events
where severity = 'critical' and created_at >= current_date - 28
group by 1 order by 1;

-- Per-agent flag rate
select a.full_name,
       count(distinct c.id) as calls,
       count(*) filter (where e.severity in ('error','critical')) as flags,
       round(100.0 * count(*) filter (where e.severity in ('error','critical')) / nullif(count(distinct c.id),0), 2) as flag_pct
from agents a
left join call_logs c on c.agent_id = a.id and c.created_at >= current_date - 7
left join compliance_audit_events e on e.agent_id = a.id and e.created_at >= current_date - 7
where a.active
group by a.full_name
order by flag_pct desc nulls last;
```

Any agent with `flag_pct > 1%` — same-day coaching, weekly recording listen.
Any agent with `flag_pct > 3%` — bench until reviewed.

### 2. Source-quality review

```sql
select source,
       count(*) leads,
       round(avg(lead_score),1) avg_score,
       sum(case when opt_out then 1 else 0 end) opt_outs,
       round(100.0 * sum(case when opt_out then 1 else 0 end) / nullif(count(*),0), 2) opt_out_pct,
       sum(case when duplicate_of is not null then 1 else 0 end) duplicates
from leads
where created_at >= current_date - 7
group by 1 order by leads desc;
```

- Opt-out rate > 8% → **pause that source for review.**
- Duplicate rate > 5% → investigate (possible scraped/farmed lead source).
- Avg score below 30 → reassess targeting.

### 3. Consent integrity scan

```sql
select * from consent_logs
where consent_type = 'multi_tpmo_share'
  and created_at >= current_date - 7
  and not fn_check_tpmo_consent_integrity(lead_id);
```

Should return zero rows. Anything here is a critical exception.

### 4. TPMO disclaimer drift check

Walk every public surface and verify the version string `tpmo-2026-04-01-v3` (or current) is what's actually showing:

- [ ] Each landing page (open in browser, view source, find `data-version`).
- [ ] Each email template (Postmark dashboard).
- [ ] Each SMS template (TCR / Twilio Messaging Service).
- [ ] TwiML on the bridge Worker (curl the TwiML endpoint, grep for the wording).
- [ ] First call script (`sales/scripts/first-call.md`).
- [ ] AI prompts (`ai/prompts/*.md`).

Any drift: stop traffic, update, re-verify.

---

## Monthly — first business day, 10:00

### 1. Recording sampling audit

Pull 25 random recordings from the prior month. Listen to 100% of each. For each, fill in a row of `compliance/audit-spreadsheet.csv` (you maintain this) with:

- call_log_id, agent_id, duration, outcome
- TPMO disclaimer in first 60 s (Y/N + timestamp)
- Recording notice acknowledged (Y/N)
- Plan/carrier named pre-SOA (Y/N)
- Savings/free claim (Y/N)
- Government implication (Y/N)
- Opt-out request handled correctly (Y/N or n/a)
- Coaching note

Aggregate Y/N counts; any row with critical Y triggers same-day investigation + agent benching.

### 2. Vendor SLA review

For each of: DNC vendor, Twilio, Postmark, OpenAI/Anthropic, transcription:

- Was the SLA met (uptime, response times)?
- Any vendor incident affecting our compliance posture?
- Any SOC 2 / DPA / BAA renewal due?

Document in `compliance/vendor-reviews/<YYYY-MM>.md`.

### 3. License + carrier appointment refresh

- Re-pull `agent_licenses` and `agent_carrier_appointments` reports.
- Cross-check 10% randomly against state DOI online verifiers (manual check — no automation can substitute).
- Flag any discrepancies for the OPS owner to remediate.

### 4. Rapid-disenrollment review

```sql
select e.agent_id, a.full_name, e.lead_id, e.carrier, e.plan_id,
       e.effective_date, e.created_at, e.status
from enrollments e join agents a on a.id = e.agent_id
where e.status = 'rapid_disenroll'
   or (e.created_at >= current_date - 90 and e.status = 'withdrawn')
order by e.created_at desc;
```

Rapid disenrollments (within 90 days of effective date) are a CMS audit trigger. Any agent with > 1/month: investigate the call recordings for high-pressure or misrepresentation flags.

### 5. Sign monthly compliance attestation

A one-page memo, signed by compliance officer, stored in `consent-evidence` bucket: month, exception summary, remediation actions, next-month focus.

---

## Quarterly — 1st of Jan / Apr / Jul / Oct

Follow the **periodic compliance officer review** procedure in `audit-procedures.md`. Output a quarterly compliance report.

---

## Pre-AEP — September 1 each year

1. Re-run `compliance/pre-launch-checklist.md` end-to-end.
2. Confirm every agent is recertified for the upcoming plan year (carrier-specific certifications, AHIP).
3. Lock all script and template changes by **September 30** — no AEP-eve edits.
4. Run `scripts/verify-deployment.sh` and ensure 100% pass.
5. Stress-test the dialer with synthetic load to 3× current peak.
6. Brief every agent in person or by recorded webinar; capture acknowledgment.

---

## Post-AEP — December 8

1. 100% audit of every enrollment from the AEP window: SOA present, agent licensed in lead's state, recording present, no rapid-disenroll signals.
2. Investigate every agent with > 2 critical events during AEP — written remediation plan or termination.
3. Source-quality retrospective: which sources delivered the best CPS at the lowest opt-out rate? Update next year's plan.
4. Refresh consent + script + template versions based on findings.

---

## Incident response playbook (use whenever)

If a beneficiary, regulator, carrier, or attorney complains:

| Step | Time | Action |
|---|---|---|
| 1 | 0–1 h | Acknowledge receipt. Lock the affected lead(s) and recording(s) (`legal_hold = true`). |
| 2 | 1–4 h | Pull every artifact: lead row, consent_logs, dnc_checks, call_logs, recordings, ai_qualification_sessions, opt_outs, compliance_audit_events. Preserve as a forensic bundle (sha256-hashed zip in `consent-evidence` bucket). |
| 3 | 4–24 h | Root-cause analysis. Was the system at fault, was an agent at fault, or is the complaint unfounded? |
| 4 | 24–72 h | Respond to complainant in writing — measured, factual, with documentation. CC counsel if it's a regulator or attorney. |
| 5 | within 7 days | Internal post-mortem. If a system fix is needed, deploy. If an agent is at fault, document discipline. If recurring pattern, update scripts + retrain. |
| 6 | within 30 days | Update SOPs / scripts / templates with lessons learned. |

---

## Tools the compliance officer needs access to

- Read access to Supabase (`compliance` JWT role).
- Read access to Postmark + Twilio dashboards (audit only — no template editing).
- Read access to the storage buckets via signed URLs.
- Read access to n8n executions (for replaying questionable runs).
- Slack channels: `#compliance-audit`, `#compliance-ai-review`, `#oncall-pages`.
- A daily 30-minute block on the calendar — **non-negotiable**, blocked for daily review.
