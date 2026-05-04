# Dialer Logic

A minimal-state, compliance-gated speed-to-lead dialer. Provider-agnostic; reference implementation uses **Twilio Programmable Voice + TwiML on a Cloudflare Worker**. Convoso, JustCall, Aircall, and ReadyMode all expose equivalent webhooks.

## Pre-call gate (hard-coded; never bypassed)

Before any outbound dial, every condition must be true. The check happens in workflow 06 against the `v_lead_reachable` view, which encodes the rules:

1. `consent_valid = true`
2. `opt_out = false`
3. `dnc_status = 'clear'` (federal DNC + state DNC + carrier suppression all clear)
4. Lead is **not** in `suppression_list` by phone_hash or email_hash
5. An active, in-state agent license exists for `lead.state`
6. Local time at the lead's timezone is between **08:00 and 21:00**
7. The dialing agent is currently **active** (not terminated/PTO) and has capacity

If any check fails, the call is not placed; the lead is queued (for time-window failures) or moved to `bucket='blocked'` (for compliance failures).

## State machine

```
                ┌────────────┐
                │  IDLE      │
                └─────┬──────┘
   workflow_06 trigger│
                     ▼
                ┌────────────┐
                │ DIALING    │ ─── timeout/no-answer ─► VOICEMAIL_DROP ─► IDLE
                └─────┬──────┘
                      │ answered
                      ▼
                ┌────────────────────┐
                │ TPMO_PLAYBACK (IVR)│  always within first 60 s
                └─────────┬──────────┘
                          │ continued press / silence-implied-OK
                          ▼
                ┌─────────────────────┐
                │ AGENT_BRIDGE         │ recording starts (record-from-answer-dual)
                └─────────┬────────────┘
                          │ end-of-call
                          ▼
                ┌─────────────────────┐
                │ POST_CALL ─► writes  │
                │   call_logs.outcome  │
                │   recordings row     │
                │   ai summarization   │
                └─────────────────────┘
```

## TPMO playback (IVR before bridge)

Twilio TwiML hosted at `${PUBLIC_BASE_URL}/twiml/medicare-bridge`:

```xml
<Response>
  <Say voice="Polly.Joanna">
    Please hold while we connect you with your licensed Medicare agent.
    We are not Medicare, the federal government, or a Medicare.gov representative.
    We do not offer every plan available in your area. Currently we represent
    multiple organizations which offer products in your area. Please contact
    Medicare dot gov, 1-800-MEDICARE, or your local State Health Insurance
    Assistance Program for all of your options. This call will be recorded
    for quality and compliance.
  </Say>
  <Pause length="1"/>
  <Dial record="record-from-answer-dual"
        recordingStatusCallback="${N8N_BASE_URL}/webhook/twilio-recording"
        callerId="${TWILIO_FROM_NUMBER}"
        timeLimit="3600"
        answerOnBridge="true">
    <Number>${AGENT_PHONE}</Number>
  </Dial>
</Response>
```

This guarantees the disclaimer is played **before** the agent ever speaks, so even if the agent forgets, the disclaimer requirement is met. Workflow 03's `tpmo_disclaimer_given=true` is set automatically by the `RecordingStatusCallback` handler, with `tpmo_disclaimer_timestamp_s ≤ 60`.

## Recording

- `record-from-answer-dual` — both legs, separate channels, starts the moment the customer answers.
- Recording finishes via `RecordingStatusCallback` → n8n stores metadata row in `recordings`, copies the file from Twilio Storage into the Supabase `call-recordings` bucket (encrypted), and sets `retention_until = call_started_at + 10 years`.
- Twilio's signed URL is captured but not used for long-term reads — recordings are read only from Supabase storage via short-lived signed URLs (≤ 15 min expiry).

## Caller ID & deliverability

- One **dedicated** outbound DID per state where you operate (or use Twilio Branded Calling / verified caller ID).
- Pre-flight: register the DID with **STIR/SHAKEN attestation A**, **CTIA / Hiya / TNS / First Orion** for spam-flag mitigation.
- Rotate DIDs at the **first sign of a spam flag**, not after.
- Never use a DID that the FCC has flagged for marketing of "Medicare benefits" by another tenant.

## Speed-to-lead targets

| Bucket | Time to first dial | Time to first SMS | Retry cadence |
|---|---|---|---|
| HOT (≥80) | ≤ 60 seconds from form submit | Concurrent | 0 / 5m / 30m / 4h / 24h / 3d |
| WARM (50–79) | ≤ 5 minutes | Concurrent | 0 / 30m / 4h / 24h / 3d / 7d |
| NURTURE (<50) | No outbound dial | Email only | 1d / 4d / 7d / 14d / 30d |

After 6 unsuccessful attempts on a HOT lead, drop to WARM cadence. After 6 unsuccessful on WARM, drop to nurture. Never exceed 7 outbound dials in any 14-day window without explicit fresh consent.

## Outbound cadence limits (TCPA-aware)

- Max 3 outbound calls per lead per day.
- Max 7 outbound calls per lead per 14-day window.
- Max 1 voicemail per day per lead.
- Calls only **08:00–21:00 lead local**, derived from ZIP → timezone (Twilio Lookup or `zipcode-to-timezone` package).
- No autodialed calls until DNC scrub completes successfully (vendor 200 OK with `clear`).

## Per-call telemetry written

Every call writes (via webhooks 06 and Twilio status callbacks):

```text
call_logs row created at dial-initiated
call_logs row updated at answered (started_at, from/to)
call_logs row updated at completed (ended_at, duration_seconds, outcome)
recordings row created at recording-completed
compliance_audit_events appended if disclaimer flag missing
ai_qualification_sessions row updated with summarization
```

## Failure handling

| Twilio event | n8n handling |
|---|---|
| `call.failed` (30-series) | Mark `outcome='failed'`, do not retry today |
| `call.busy` | Mark `outcome='busy'`, retry per cadence |
| `call.no-answer` | VM drop (if first attempt of the day), retry |
| `call.completed duration<5s` | `outcome='dropped'`, alert ops |
| `recording-completed missing url` | `recording_missing` audit event, page on-call |
