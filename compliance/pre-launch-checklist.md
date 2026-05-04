# Pre-launch Compliance Checklist

Every box must be checked before the first real lead enters the system. Re-run this whenever any of the items materially change.

## Legal & registration

- [ ] Agency entity is properly licensed in **every state** where you intend to acquire and convert leads.
- [ ] Each agent has active state licenses recorded in `agent_licenses` with valid `expires_at` dates.
- [ ] Each agent has carrier appointments in `agent_carrier_appointments` for at least the carriers they'll quote.
- [ ] Each agent has completed AHIP (or equivalent annual recertification) for the current plan year.
- [ ] Each agent has carrier-specific certifications for the current plan year.
- [ ] FMO contract reviewed; no FMO term blocks owned-funnel marketing or requires lead sharing without itemized consent.
- [ ] Errors & Omissions insurance current and adequate.
- [ ] Business has registered with state DOI as required (some states require TPMO/marketer registration explicitly).

## Telephony & messaging

- [ ] 10DLC brand registered, campaign approved for "insurance lead nurture" or equivalent.
- [ ] STIR/SHAKEN attestation level A on every outbound DID.
- [ ] Twilio "Trust Hub" / dialer provider's compliance settings completed.
- [ ] Caller ID per-state DIDs provisioned and verified.
- [ ] Federal DNC vendor active; subscription current; vendor SLA documented.
- [ ] State-DNC scrubs configured for every state where stricter rules apply (e.g., FL, TX, IN).
- [ ] Litigator scrub active.
- [ ] Internal `suppression_list` populated with prior opt-outs and any known-bad numbers.
- [ ] TCPA call-time enforcement (08:00–21:00 lead-local) verified in workflow 06 with simulated calls in 4 timezones.
- [ ] SMS templates approved by 10DLC reviewer; each template includes opt-out instruction.

## Recording

- [ ] Recording bucket `call-recordings` created in Supabase Storage, encryption at rest enabled.
- [ ] Bucket lifecycle 10-year retention configured.
- [ ] Two-party-consent states identified; IVR disclaimer plays the recording notice in every outbound + inbound call.
- [ ] Test calls in dev: full recording uploaded to Supabase, checksum matches, retention set, RLS allows compliance reads, denies anon reads.
- [ ] Subpoena export workflow tested with a synthetic case.

## Data & infrastructure

- [ ] Supabase migrations 0001–0006 applied successfully.
- [ ] RLS verified — agent JWT can read only their leads, recordings, calls; service role can; anon can only read campaigns.
- [ ] Storage bucket policies in place for `call-recordings`, `consent-evidence`, `soa-evidence`.
- [ ] `evidence_hash` computed and reproducible client-side and server-side (HMAC test passes).
- [ ] All n8n workflows imported, credentials set, activated.
- [ ] WAF / Turnstile in front of the lead-capture endpoint; HMAC signing in place.
- [ ] Backups: daily Supabase backup, weekly recording-bucket snapshot, monthly cold-archive of consent logs.

## TPMO & marketing

- [ ] TPMO disclaimer wording (`tpmo-2026-04-01-v3`) deployed on every landing page above the fold.
- [ ] TPMO disclaimer in TwiML IVR playback verified (auditable via test recording).
- [ ] Email footer carries TPMO disclaimer.
- [ ] SMS templates carry the truncated disclaimer.
- [ ] No prohibited claims in any active ad creative (run `compliance-auditor.md` audit on creative).
- [ ] No flag-blue/Medicare-card iconography in any creative.
- [ ] `consented_entities` includes only your agency unless a partner TPMO has been added with separate checkbox.
- [ ] Privacy policy, terms, accessibility statement live and dated.
- [ ] State-specific disclosures present where required (e.g., CA Privacy Rights, "Do Not Sell or Share").

## Sales operations

- [ ] All 9 sales scripts reviewed by compliance and signed off.
- [ ] Agent training completed for every agent.
- [ ] First-5-calls review process in place for new agents.
- [ ] Daily compliance audit (workflow 10) configured and tested with synthetic data.
- [ ] Campaign reporting (workflow 11) configured; KPI dashboard (Metabase or equivalent) live.
- [ ] On-call rotation defined for compliance pages.

## Acceptance test (do not skip)

- [ ] Submit a test lead through the live landing page. Verify:
  - Lead row created with `consent_valid=true`, `dnc_status` resolves, `lead_score` computed.
  - `consent_logs` rows for tcpa_phone, recording_notice, tpmo_disclosure, plus per-entity rows.
  - `compliance_audit_events` rows for each gate decision.
  - HOT lead triggers a real outbound call; recording uploads; TPMO disclaimer is in the recording's first 60 s.
  - Reply STOP to the SMS — workflow 09 propagates within 60 s; subsequent dial attempts are blocked.
  - End-to-end timing: form submit → outbound dial < 60 s for HOT.
- [ ] Run the compliance auditor (`audit-v1`) over the test artifacts; zero critical exceptions.
