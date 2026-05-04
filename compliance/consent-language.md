# Consent Language — Canonical Block

The TCPA, the FCC's prior-express-written-consent rule, and CMS's MCMG together set the bar. We write to the higher of all three.

## The required components in any prior express written consent (PEWC)

A valid PEWC must:

1. Be **written**, signed (electronic signature counts) by the consumer.
2. Authorize calls/texts to a **specific phone number**.
3. Be **clear and conspicuous** — not buried in a long block of text.
4. Disclose that the calls/texts may be made by **automatic telephone dialing system** and/or **prerecorded/artificial voice**.
5. State that consent is **not a condition of any purchase**.
6. Identify the **specific seller(s)** authorized to call. **Each receiving entity must be listed with an individual checkbox** when more than one exists.

## Canonical block (current version: `consent-2026-04-01-v2`)

> By checking this box and clicking submit, I authorize **{AGENCY_NAME}** (the receiving party named below) and the licensed agent assigned to me to contact me at the phone number and email I provided, including by automatic telephone dialing system, prerecorded/artificial voice, SMS text message, and email, regarding Medicare insurance products. Message and data rates may apply. Reply STOP to opt out. **Consent is not a condition of any purchase.** [Privacy Policy].
>
> **Receiving entities (your express consent applies only to those you check):**
> - [ ] {AGENCY_NAME} (the agency you're contacting)
> - [ ] *(only if applicable — list each partner TPMO individually with its own checkbox)*

## What to record (every consent insert)

`consent_logs` row must capture:

- `consent_type` — `'tcpa_phone'` for the form-signed PEWC; additional rows for `'tcpa_sms'`, `'email_marketing'`, `'recording_notice'`, `'tpmo_disclosure'`, `'multi_tpmo_share'`.
- `consent_text` — the **exact** wording the consumer saw, full text, no truncation.
- `consent_version` — see version block above.
- `ip_address`, `user_agent`, `landing_page_url` — captured server-side at webhook ingest.
- `consented_entities` — JSON array `[{name, role, accepted}]` matching every checkbox state.
- `evidence_hash` — sha256 of the canonical evidence payload (computed in `consent-tracker.js`, recomputed server-side, must match).

## Multi-TPMO sharing

If your business model shares lead data with another TPMO (e.g., another agency or marketing partner), CMS requires the lead's prior express written consent to specifically list each receiving entity. **Bundled consent is non-compliant.**

Implementation:

- Each partner gets its own `<input type="checkbox" data-entity="...">` with its own checkbox.
- The default state is unchecked (no pre-checked partner boxes).
- The lead must affirmatively check at least your agency before submit; partners are optional.
- `fn_check_tpmo_consent_integrity` (migration 0004) validates the JSONB `consented_entities` shape nightly and fails any record without each entity tagged with `accepted: bool`.

## Recording-notice consent

A separate checkbox with this language:

> *"I understand calls may be recorded for quality and compliance."*

This is captured as a `consent_logs` row of type `recording_notice` so we have form-time evidence for two-party-consent states.

## Revocation

A consumer can revoke consent any time via any reasonable means. Workflow 09 picks up:

- Inbound SMS containing STOP/UNSUBSCRIBE/CANCEL/END/QUIT/REMOVE/"do not call".
- Inbound email to the unsubscribe alias or one-click `List-Unsubscribe-Post` headers.
- Voice DTMF (1-press) on outbound voicemail platform.
- Manual entry by an agent in the CRM.
- Postal mail to our published address (manual entry in CRM by ops).

Revocation propagation must complete within minutes across all systems. The daily audit (workflow 10) verifies opt-outs are honored — any contact after `opt_out_at` is `event_type='opt_out_leak'` and `severity='critical'`.

## Versioning

- `consent-2024-10-01-v1` — initial.
- `consent-2026-04-01-v2` — current. Adds explicit per-entity checkbox structure.
