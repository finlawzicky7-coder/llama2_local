# Architecture

## End-to-end data flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ACQUISITION SURFACES                                                    │
│  Google Search Ads · Local SEO · Education funnels · Meta retargeting    │
│  YouTube education · Referral · Community events · Direct mail QR · CRM │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  LANDING PAGES (Cloudflare Pages / Vercel)                               │
│  • TPMO disclaimer above the fold                                        │
│  • Education-first hero + benefits-neutral copy                          │
│  • Consent block: TCPA + TPMO + listed entities + version hash           │
│  • Turnstile/hCaptcha + UTM + IP + UA capture                            │
│  • consent-tracker.js posts payload + hashed evidence to webhook         │
└──────────────────────────────────────────────────────────────────────────┘
                                   │  HTTPS POST
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  n8n WORKFLOW 01 — Lead Capture Webhook                                  │
│  validates schema, normalizes phone (E.164), upserts lead, writes        │
│  consent_logs with full evidence, fires compliance_audit_event           │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  n8n WORKFLOW 02 — Compliance Gate                                       │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │ 1. Internal opt-out lookup                                       │    │
│  │ 2. Federal DNC scrub + state DNC where required                  │    │
│  │ 3. Litigator/known-bad list scrub                                │    │
│  │ 4. Carrier suppression list scrub                                │    │
│  │ 5. State licensing — does an active agent cover lead.state?      │    │
│  │ 6. Consent freshness check (≤ retention policy window)           │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│  PASS → leads.dnc_status='clear', proceed                                │
│  FAIL → log compliance_audit_event, suppress, route to nurture only      │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  n8n WORKFLOW 03 — AI Qualification                                      │
│  • Inbound chat OR text-back triage OR voice agent                       │
│  • Confirms what they asked for, identifies as NOT Medicare/CMS          │
│  • Plays TPMO disclaimer; collects qual fields                           │
│  • Returns JSON {qualified, intent_score, summary, compliance_flags}     │
│  • Persists ai_qualification_sessions row                                │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  n8n WORKFLOW 04 — Lead Scoring                                          │
│  weighted score = recency × intent × Medicare-status × source-quality    │
│  × geo-licensing × time-of-day × consent-strength                        │
│  buckets: HOT (≥80) · WARM (50–79) · NURTURE (<50)                       │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  n8n WORKFLOW 05 — Agent Routing                                         │
│  state-licensed + active + capacity + carrier appointment + skill match  │
│  HOT → instant assign + push to dialer; WARM → next-available queue;     │
│  NURTURE → drip cadence only                                             │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  n8n WORKFLOW 06 — Dialer Trigger (Speed-to-Lead)                        │
│  Twilio/Convoso outbound, agent-bridge, recording_url returned           │
│  TPMO disclaimer played in first minute, full call recorded              │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  n8n WORKFLOW 07 — Multi-channel Follow-up Cadence                       │
│  missed-call SMS, email, voicemail-drop (with disclaimer), retry         │
│  windows respect TCPA call-time rules per lead's local timezone          │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  n8n WORKFLOW 08 — Appointment Booking                                   │
│  Cal.com / Google Calendar; SOA flow before any plan-specific            │
│  conversation; confirmations + reminders                                 │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW 09 — Opt-out Suppression (always-on listener)                  │
│  inbound SMS STOP / email unsub / dialer STOP / chat opt-out             │
│  → opt_outs row, leads.opt_out=true, suppress all channels, ack          │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW 10 — Daily Compliance Audit (cron 03:00 local)                 │
│  detects missing TPMO disclaimers, missing recordings, expired consents, │
│  unlicensed-state outreach, multi-TPMO consent integrity, opt-out leaks  │
│  emits exception report + locks offending leads                          │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW 11 — Campaign Performance Reporting (hourly + daily)           │
│  CPL · CPA · CPS · contact rate · quote rate · enrollment rate · LTV     │
│  by source/campaign/agent/state/product → dashboard + Slack digest       │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  AI OPTIMIZATION LOOP                                                    │
│  daily summary → bid/budget adjustments, script variants, scoring        │
│  weights, cadence tuning, agent feedback                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

## Service responsibilities

| Surface | Responsibility |
|---|---|
| Landing pages | Education-first content, consent capture, TPMO disclaimer, evidence collection |
| Cloudflare Turnstile | Bot mitigation before form submit |
| n8n | Orchestration of every cross-system action; the only writer to Supabase from the front edge |
| Supabase Postgres | Source of truth for leads, consents, calls, recordings metadata, audits |
| Supabase Storage | Encrypted call recordings (versioned bucket, lifecycle 10y, signed URLs only) |
| Supabase Edge Functions | Hashing utilities, signed-URL minting for recordings, light webhook validators |
| Twilio / Dialer | Outbound calling, IVR for TPMO playback, call recording, webhooks back into n8n |
| OpenAI / Anthropic | LLM endpoints for qualification, summarization, scoring, audit pattern detection |
| Cal.com | Appointment scheduling with SOA pre-flow |
| BigQuery / Metabase | Analytics warehouse for the optimization loop |

## Trust boundaries

- **Internet → Webhook:** WAF + Turnstile + HMAC signature on all inbound webhooks; rate-limit per IP + per phone hash.
- **n8n → Supabase:** service-role JWT scoped per workflow; never embed in browser; rotated quarterly.
- **Supabase → Storage:** call recordings stored encrypted at rest, accessed only via short-lived signed URLs; access logged in `compliance_audit_events`.
- **Agents → CRM:** agents authenticate via SSO; RLS confines them to leads where `assigned_agent_id = auth.uid()` (see migration 0004).
- **PII handling:** no full DOB stored unless required for enrollment; phone/email hashed in DNC vendor calls; recordings retained per CMS retention guidance.

## Failure modes & guardrails

| Failure | Detection | Response |
|---|---|---|
| Webhook missing consent fields | schema validator in workflow 01 | 400 + audit event, no row inserted |
| DNC vendor 5xx | retry + circuit breaker | hold lead in `pending_compliance`, retry hourly, never auto-pass |
| Unlicensed state | routing query returns 0 agents | move to nurture, alert ops |
| Recording upload failed | dialer webhook missing `recording_url` | mark call `recording_missing`, daily audit flags it |
| LLM hallucinates plan name | compliance flag scanner in workflow 03 | downgrade to human, lock AI session, alert compliance |
| Opt-out not propagated within 5 min | listener heartbeat check | page on-call, halt outbound for that lead globally |

## Environments

- **dev** — Supabase branch + n8n local + Twilio test creds + OpenAI dev key.
- **staging** — production-equivalent; synthetic leads only; dialer in record-only sandbox.
- **prod** — locked behind change-management; migrations applied via PR + reviewer; secrets in n8n + Supabase Vault, never in workflow JSON.
