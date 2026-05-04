# Call Recording & Retention Policy

CMS expects TPMOs to **record all calls (in their entirety) related to the marketing, sales, and enrollment of Medicare Advantage and Part D plans**. This policy is built around that requirement and applies the higher of CMS, FCC, FTC, and state requirements.

## What we record

| Call type | Record? | Retention |
|---|---|---|
| Outbound speed-to-lead dial (any duration) | Yes — both legs | 10 years |
| Inbound to a published marketing line | Yes — both legs | 10 years |
| Voice-AI confirmation call | Yes — agent-side at minimum, plus AI transcript | 10 years |
| Internal coaching call between agents | Yes (state-law-permitting), separate bucket | 7 years |
| HR / personal calls | No | n/a |

## How we record

- Provider records both legs in dual channel (`record-from-answer-dual` on Twilio).
- Recording starts at **answer**, before the agent ever speaks. The TPMO playback IVR is therefore inside the recording.
- Recordings are pulled from the provider's storage to **Supabase Storage `call-recordings` bucket** within 15 minutes of `recording-completed`, encrypted at rest (AES-256), accessed only via short-lived signed URLs (≤ 15 minutes).
- A SHA-256 checksum is stored at upload to detect tampering.

## Disclosure to the called party

Two layers of disclosure:

1. **Web form** — explicit consent checkbox: *"I understand calls may be recorded for quality and compliance."*
2. **Call** — the IVR plays the disclaimer including *"This call will be recorded for quality and compliance"* before the agent bridges in.

Two-party-consent states (CA, FL, IL, MD, MA, MT, NH, PA, WA, plus others) are covered by the IVR notice + form consent.

## Storage & access controls

- Bucket policy: only `service_role` and `compliance` JWTs may read. `agent` role can request a signed URL only for recordings on calls they were the bridged agent on (RLS on `recordings` ties to `call_logs.agent_id`).
- Recordings are **never** delivered as raw URLs to the browser — always as one-shot signed URLs.
- Every signed-URL mint writes a `compliance_audit_events` row (`event_type='recording_access'`, `severity='info'`, `details={agent_id, call_log_id, ip}`).

## Retention & legal hold

- Default retention: **10 years** (`recordings.retention_until = call_started_at + 10 years`).
- Legal hold: setting `recordings.legal_hold = true` overrides the lifecycle deletion. Only compliance role + ops admin can set this.
- A daily cron (extension of workflow 10) deletes recordings whose `retention_until < today` AND `legal_hold = false`. Deletion writes an `event_type='retention_deletion'` audit event and removes both the row and the storage object.

## Subpoena / regulator request workflow

When a regulator (CMS, state DOI, FTC, FCC) or a subpoena requests recordings:

1. Compliance officer flips `legal_hold = true` on the affected `recordings` rows.
2. Compliance opens a ticketed export: signs URLs with extended TTL (e.g., 24h), zips them, hashes the bundle, and delivers via the regulator's secure channel.
3. Audit event: `event_type='regulator_export'` with payload `{requestor, scope, sha256_bundle}`.

## Privacy

- Recordings are **business records of a regulated communication**, not HIPAA records by themselves. Treat them with HIPAA-equivalent care anyway: encryption at rest, encryption in transit, least-privilege access.
- We do **not** transcribe recordings to third-party services that retain content. Our transcription provider must offer a zero-retention or signed-BAA configuration. (Whisper deployed within Supabase Edge Functions or Deepgram with zero-retention.)
- Transcripts are stored in `call_logs.transcript`. They are accessed under the same RLS as the `recordings` row.

## What never gets recorded

- Application form fills (we have the typed evidence; recording adds nothing).
- Internal Slack chats, email — those are governed by separate retention policies.
- Agent's personal conversations.

## Test plan (run before AEP each year)

- [ ] End-to-end: simulate a HOT lead, confirm IVR plays disclaimer in the first 60 s.
- [ ] Recording arrives in Supabase, checksum matches, retention set to 10y.
- [ ] Compliance role can read; agent role can read only their own; anon cannot read.
- [ ] Lifecycle deletion fires only on rows with no legal hold and `retention_until < today`.
- [ ] Subpoena export workflow exercised with a synthetic case.
