# Compliance Checklist (system-wide)

> This is the system-level checklist. Pre-launch operational checklist lives at `compliance/pre-launch-checklist.md`. Audit procedures at `compliance/audit-procedures.md`. TPMO wording at `compliance/tpmo-disclaimer.md`. Consent block at `compliance/consent-language.md`.

## CMS / MCMG (Medicare-specific)

- [ ] Treat the agency as a TPMO. All marketing surfaces carry the disclaimer.
- [ ] Disclaimer appears within the first **60 seconds** of every marketing/sales/enrollment call.
- [ ] Disclaimer appears prominently on every landing page above the fold.
- [ ] No claims of being Medicare, the federal government, or Medicare.gov.
- [ ] No "best plan", "guaranteed savings", "free benefits", "extra money", "everyone qualifies" language.
- [ ] No specific plan or benefit recommendations made by AI agents at any time.
- [ ] No specific plan or benefit recommendations made by human agents until SOA is signed.
- [ ] Multi-TPMO data sharing (if any) requires individual checkbox per receiving entity in the consent flow.
- [ ] Every marketing/sales/enrollment call recorded in entirety and retained 10 years.
- [ ] Pre-enrollment checklist completed before any application; no application "from memory."
- [ ] Scope of Appointment captured before plan-specific conversation; SOA evidence archived.
- [ ] Rapid-disenrollment monitoring active (within 90 days of effective date).

## TCPA / FCC

- [ ] Prior express written consent on file for every contacted lead, with text, version, IP, UA, page URL.
- [ ] Consent specifies: ATDS / prerecorded / SMS / email; named seller(s); not a condition of purchase; STOP to opt out.
- [ ] Each receiving entity (agency + any partner TPMOs) has an individual checkbox; no bundled consent.
- [ ] Outbound only between 08:00 and 21:00 lead-local.
- [ ] STIR/SHAKEN attestation A on every DID.
- [ ] 10DLC brand registered, campaign approved.
- [ ] Federal DNC scrub pre-call; state DNC scrubs where required; vendor SLA documented.
- [ ] Litigator/known-bad scrub active.
- [ ] Opt-out propagation within minutes across all channels.

## State (varies)

- [ ] Two-party-consent state recording handled by IVR + form consent.
- [ ] State-level marketing disclosures (e.g., FL, NY) added where required.
- [ ] State-level DNC subscriptions where stricter than federal.
- [ ] State-level licensing per agent and per agency.

## HIPAA / privacy

- [ ] Beneficiary data encrypted at rest and in transit.
- [ ] Access logged at every read of recordings, transcripts, and consent evidence.
- [ ] PII collection minimized: phone, email, ZIP, state, Medicare status, optional birth month/year. No full DOB or full SSN at lead intake.
- [ ] Vendor agreements (transcription, voice AI) have zero-retention or BAA.
- [ ] Subpoena workflow established; legal hold mechanism in place.
- [ ] Breach response runbook in place.

## FMO / carrier

- [ ] Any required FMO marketing-material approvals completed.
- [ ] Carrier-specific marketing rules followed (often stricter than CMS).
- [ ] Annual recertifications and AHIP current for every agent.

## Operational hygiene

- [ ] Daily compliance audit (workflow 10) running; Slack digest delivered.
- [ ] AI compliance auditor (`audit-v1`) running on prior-day artifacts.
- [ ] On-call rotation defined; pages tested.
- [ ] Quarterly compliance review calendared.
- [ ] Pre-AEP and post-AEP audits calendared.
- [ ] All scripts and templates under version control with compliance sign-off on PRs.
