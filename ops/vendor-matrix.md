# Vendor Selection Matrix

Concrete recommendations for each component, with the criteria that matter for a **TPMO-compliant Medicare lead engine**. Pick one per row. Renegotiate annually.

---

## Database / auth / storage

| Vendor | Use? | Notes |
|---|---|---|
| **Supabase** | ✅ default | Postgres + RLS + Storage + Auth + Edge Functions in one. Pro plan ($25/mo + usage) supports HIPAA add-on if needed (BAA). |
| Neon + Auth0 + S3 | alternative | More moving parts. Use only if you already run on AWS. |
| RDS + Cognito + S3 | alternative | Most flexible, most ops overhead. |

**Hard requirement:** encryption-at-rest, point-in-time recovery, signed-URL storage, audit logs on row reads of sensitive tables.

---

## Workflow orchestration

| Vendor | Use? | Notes |
|---|---|---|
| **n8n self-hosted** | ✅ default | Deterministic, no per-execution cost, easy to fork the JSON. Run on Fly.io or a small EC2 ($20–$60/mo). |
| n8n Cloud | alt | Same product; pricier; saves you ops time. |
| Zapier / Make | ❌ | No HMAC verification on webhooks, no first-class queue depth, not auditable enough for compliance work. |
| Temporal | alt for scale | When you outgrow n8n at >100k leads/month, port the workflows to Temporal for durability. |

---

## Telephony / dialer

| Vendor | Use? | Notes |
|---|---|---|
| **Twilio Programmable Voice** | ✅ default for engineering teams | Best APIs, native recording, easy to enforce IVR-disclaimer-before-bridge. ~$0.0085/min outbound + recording storage. |
| **Convoso** | alt for predictive dialing | More turnkey for a 10+ agent room. Has its own compliance posture; verify TPMO-disclaimer playback before bridge is configurable. |
| **JustCall / Aircall** | ❌ for primary dialer | Built for general sales, not for Medicare's recording + disclosure requirements. |
| **ReadyMode** | alt | Insurance-industry-tuned. Verify it lets you enforce the IVR pre-bridge. |

**Hard requirements:** STIR/SHAKEN attestation A on every DID, dual-channel recording, webhook on recording-completed, ability to insert a TwiML/IVR step before the agent bridges.

---

## SMS

| Vendor | Use? | Notes |
|---|---|---|
| **Twilio 10DLC + verified TF** | ✅ default | Use 10DLC for marketing campaigns; toll-free verified for transactional (appointment confirmations). |
| Telnyx | alt | Cheaper per-message; less mature compliance UI. |

**Hard requirement:** brand verification (TCR), campaign approval for "insurance lead nurture," opt-out keyword auto-handling routed to your webhook 09.

---

## Email

| Vendor | Use? | Notes |
|---|---|---|
| **Postmark** | ✅ default for transactional + small-list marketing | Strict on spam, fast, easy template aliases. Use **two streams:** `medicare-broadcast` and `medicare-transactional`. |
| SendGrid | alt | Cheaper at high volume; spam-rep more variable. |
| Mailchimp / Klaviyo | ❌ | Too marketer-friendly; not enough deliverability discipline for Medicare. |

**Hard requirements:** SPF/DKIM/DMARC aligned (`p=reject`), List-Unsubscribe header + One-Click POST, separate streams for marketing vs transactional, 30-day bounce + complaint reports stored in `compliance_audit_events`.

---

## DNC / suppression

| Vendor | Use? | Notes |
|---|---|---|
| **Contact Center Compliance (DNC.com)** | ✅ default | Federal + state DNC + litigator + carrier suppression in one API. ~$200–$500/mo. |
| **Gryphon** | alt | Similar coverage; enterprise-grade; more expensive. |
| **DNCcheck** | alt | Lighter / cheaper; verify state coverage matches your launch states. |

**Hard requirement:** API returns federal DNC + each state DNC where you operate + a known-litigator list, with vendor liability commitment for stale data.

---

## Voicemail drop (RVM)

| Vendor | Use? | Notes |
|---|---|---|
| **Slybroadcast** | ✅ if used | Carrier-friendly RVM. Use sparingly — ringless voicemail is in regulatory gray zone in some states; many TCPA suits target it. |
| **VoApps RVM** | alt | Higher-end; carrier relationships. |
| **None** | ✅ acceptable | Many compliance officers prefer not to use RVM at all. The cadence works without it. |

**Hard requirement (if used):** documented carrier-of-record relationships; consent-based recipients only; clear opt-out handling.

---

## LLM provider

| Vendor | Use? | Notes |
|---|---|---|
| **OpenAI (gpt-4.1-mini, gpt-4.1)** | ✅ default | Reliable JSON mode, cheap mini tier for qualification. **Set zero data retention via the Enterprise / API DPA.** |
| **Anthropic Claude (Haiku 4.5, Sonnet 4.6)** | ✅ alt | Excellent at compliance auditing; tool-use to coerce JSON. Confirm zero retention contract. |
| Self-hosted Llama / Mistral | alt | Strongest privacy posture; engineering overhead; lower quality on subtle compliance flags. |

**Hard requirement:** zero-retention configuration in writing. PII in prompts is a compliance risk if the vendor trains on it.

---

## Voice AI (callback confirmation only)

| Vendor | Use? | Notes |
|---|---|---|
| **Vapi** | ✅ default | Built for low-latency phone bots; bring-your-own LLM and voice. |
| **Retell AI** | alt | Similar; nice agent-builder UI. |
| **LiveKit Agents** | alt | More control; higher engineering cost. |
| **ElevenLabs Conversational** | alt | Best voice quality; verify recording + interrupt handling. |

**Constraint:** AI voice for **confirmation calls only**, never sales/enrollment. See `ai/prompts/voice-agent.md`.

---

## Transcription

| Vendor | Use? | Notes |
|---|---|---|
| **Deepgram (zero-retention contract)** | ✅ default | Fast, accurate, reasonable price, contractable. |
| Whisper self-hosted | alt | Highest privacy; more ops. |
| AssemblyAI | alt | Good UI; verify zero-retention. |

**Hard requirement:** zero-retention or BAA. Recordings + transcripts cannot leak into a vendor training set.

---

## Scheduling

| Vendor | Use? | Notes |
|---|---|---|
| **Cal.com (cloud or self-hosted)** | ✅ default | Open source, API-first, calendar integrations. |
| Calendly | alt | Closed source, harder to embed conditional logic (SOA pre-flow). |

---

## CDN / WAF / form proxy

| Vendor | Use? | Notes |
|---|---|---|
| **Cloudflare (Pages + Workers + Turnstile + WAF)** | ✅ default | Bot mitigation, free tier covers your launch volume, Workers for the HMAC proxy. |
| Vercel + reCAPTCHA Enterprise | alt | More expensive; reCAPTCHA Enterprise is fine. |

---

## Errors / observability

| Vendor | Use? | Notes |
|---|---|---|
| **Sentry** | ✅ default | Workflow JSON parsers, Worker errors, client-side form errors. |
| Datadog | alt at scale | When you need traces across n8n + Twilio + Supabase + ad APIs. |

---

## Analytics / BI

| Vendor | Use? | Notes |
|---|---|---|
| **Metabase (self-hosted)** | ✅ default | Free, points at Supabase Postgres directly, builds dashboards on `v_kpi_daily` and `v_agent_funnel`. |
| Looker Studio | alt | Free, but you'll need a connector. |
| Mode / Hex | alt for analyst-led teams | Better SQL UX, more $. |

---

## On-call paging

| Vendor | Use? | Notes |
|---|---|---|
| **PagerDuty** | ✅ default | Slack webhook → PD service for `severity in ('error','critical')` audit events. |
| Opsgenie | alt | If already on Atlassian. |
| Slack alone | ❌ | Slack alone is not a pager. Use Slack for digests, PD for criticals. |

---

## E&O insurance

| Vendor | Use? | Notes |
|---|---|---|
| Hiscox / Travelers / Chubb (via your FMO) | ✅ via your broker | Carry **at least** $1M / $2M aggregate. Increase before AEP. |

---

## Compliance counsel

| Vendor | Use? | Notes |
|---|---|---|
| Health-insurance-savvy outside counsel on retainer | ✅ required | $5–$15k/year retainer for quick reads on disclosures, MCMG updates, beneficiary complaints. |

---

## Annual budget rough order

| Bucket | Year 1 | At scale (10k leads/mo) |
|---|---|---|
| Supabase | $300–$1,200 | $3,000 |
| n8n self-host | $300 | $1,500 |
| Twilio (voice + SMS) | $2k–$10k | $40k+ |
| OpenAI / Anthropic | $500–$3k | $10k+ |
| DNC vendor | $2,500 | $6,000 |
| Postmark | $360 | $4,000 |
| Cloudflare | $0–$240 | $1,200 |
| Cal.com self-host | $0 | $300 |
| Sentry / PD | $300 | $2,400 |
| E&O insurance | $1,500 | $5,000+ |
| Outside counsel | $5,000 | $15,000 |
| **Subtotal infra/compliance** | **~$13k–$25k** | **~$90k–$120k** |

(Ad spend, lead generation, and agent salaries are separate.)
