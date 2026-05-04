# Audit Procedures

Two layers of audit:

1. **Continuous** — workflow 10 runs at 03:00 daily; AI compliance auditor runs at 04:00 daily over yesterday's artifacts.
2. **Periodic** — quarterly compliance officer review; pre-AEP full audit; post-AEP retrospective.

## Continuous (automated)

### Daily compliance audit (workflow 10)

Detects within the previous 24h:

| Check | What it does | Severity |
|---|---|---|
| Missing TPMO disclaimer | Calls with `outcome IN ('connected','appointment_set','sold')` and `tpmo_disclaimer_given=false` | critical |
| Missing recording | Same calls without a `recordings` row | critical |
| Opt-out leak | Any call started after a lead's `opt_out_at` | critical |
| Unlicensed outreach | Calls where the agent didn't have an active license in the lead's state | critical |
| Multi-TPMO consent integrity | `fn_check_tpmo_consent_integrity` returns false for any consent_logs row | critical |
| License expiring within 30 days | `agent_licenses.expires_at < today + 30d` | warn |

Output: `compliance_audit_events` rows + Slack digest at 03:15.

### Daily AI compliance auditor (`audit-v1`)

Pulls 100% of yesterday's call transcripts, all active landing pages, all SMS/email templates, and all ad creatives changed in the last 7 days. Returns a structured exception JSON; rows are inserted into `compliance_audit_events`. Critical exceptions auto-page on-call.

### Real-time triggers (Postgres)

- `trg_audit_opt_out` fires on `leads.opt_out` flip → audit event.
- `trg_audit_call_disclaimer` fires on `call_logs.ended_at` set → audit event if disclaimer missing.
- `trg_license_expiration` fires on `agent_licenses` insert/update → warning event if `expires_at <= today + 30 days`.

## Periodic (manual)

### Quarterly compliance officer review

Compliance officer reviews:

- 5 randomly-sampled call recordings per agent (use Supabase signed URLs).
- 100% of `compliance_audit_events` with `severity IN ('error','critical')` from the period.
- All ad creative variants run during the period.
- All script variants modified during the period.
- All consent template diffs.
- All licensing changes (new hires, terminations, expirations).
- One simulated end-to-end test lead.

Output: a quarterly compliance report stored in `consent-evidence` bucket, signed by the compliance officer.

### Pre-AEP audit (mid-September)

- Re-run the full pre-launch checklist (`pre-launch-checklist.md`).
- Validate every state license against the state DOI's online verifier (manual).
- Validate every carrier appointment against the carrier's broker portal.
- Refresh DNC vendor subscription.
- Spot-check 5% of consents from the past 90 days for completeness.
- Lock all script and template changes 7 days before Oct 15.

### Post-AEP retrospective (mid-December)

- Audit 100% of enrollments for SOA presence, agent licensing alignment, recording presence, and disclosure.
- Investigate any rapid disenrollments (under 90 days from effective date) — those are CMS audit triggers.
- Investigate any agent with > 2 critical compliance flags during AEP.
- Update consent + script templates based on findings; retrain.

## Incident response

For any **critical** severity event:

1. **Within 1 hour:** on-call confirms the incident, locks the affected lead(s) (`bucket='blocked'`), stops further outreach.
2. **Within 4 hours:** root cause identified; if it's a code/workflow bug, deploy the fix; if it's an agent error, the agent is benched pending review.
3. **Within 24 hours:** remediation note added to the affected leads; consent/recording evidence preserved; affected lead(s) given the option to be removed entirely.
4. **Within 7 days:** post-mortem written, signed by compliance officer, stored in compliance audit log.
5. **Reportable events** (regulator inquiry, beneficiary complaint, CMS finding) escalate to legal counsel.

## Documentation retention

| Artifact | Retention | Storage |
|---|---|---|
| Call recordings | 10 years | `call-recordings` bucket (Supabase) |
| Consent logs | 10 years | `consent_logs` table + nightly export to `consent-evidence` bucket |
| Compliance audit events | 10 years | `compliance_audit_events` table |
| SOA records | 10 years | `soa_records` table + `soa-evidence` bucket |
| Quarterly compliance reports | 10 years | `consent-evidence` bucket, immutable |
| Post-mortems | Indefinite | Internal compliance wiki |
