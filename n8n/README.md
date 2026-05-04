# n8n Workflows

Eleven importable workflow JSON files. Import in order:

| # | Name | Trigger | Purpose |
|---|---|---|---|
| 01 | Lead Capture | Webhook `POST /medicare-lead-capture` | HMAC-verified inbound from landing pages → insert lead + consent log |
| 02 | Compliance Gate | Webhook `POST /medicare-compliance-gate` | Suppression + DNC + license coverage |
| 03 | AI Qualification | Webhook `POST /medicare-ai-qualify` | LLM qualification + flag scan + persistence |
| 04 | Lead Scoring | Webhook `POST /medicare-score-lead` | `fn_score_lead` + bucketization |
| 05 | Agent Routing | Webhook `POST /medicare-route-lead` | `fn_route_lead` + assignment + dispatch |
| 06 | Dialer Trigger | Webhook `POST /medicare-dial` | Reachability + TCPA window + Twilio dial-bridge |
| 07 | Follow-up Cadence | Webhook `POST /medicare-followup-cadence` | SMS / email / VM cadence honoring opt-out |
| 08 | Appointment Booking | Webhook `POST /medicare-book-appointment` | Cal.com booking + confirmation + SOA link |
| 09 | Opt-out Listener | Webhook `POST /medicare-optout` | STOP/unsub propagation across channels |
| 10 | Daily Compliance Audit | Cron `0 3 * * *` | Detect TPMO/recording/consent/license breaches |
| 11 | Campaign Reporting | Cron `0 * * * *` | KPI digest to Slack |

## Required environment variables (n8n → Settings → Variables)

```
SUPABASE_URL                    https://<project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY       (secret)
N8N_BASE_URL                    https://n8n.your-domain.com
N8N_INTERNAL_TOKEN              (secret, used by workflows calling each other)
WEBHOOK_HMAC_SECRET             (secret, shared with landing-page consent-tracker.js)
PUBLIC_BASE_URL                 https://api.your-domain.com  (TwiML host)
PUBLIC_HOST                     www.your-domain.com

OPENAI_API_KEY                  (or ANTHROPIC_API_KEY if you swap nodes)
AI_QUAL_SYSTEM_PROMPT           paste from ai/prompts/qualification-agent.md

TWILIO_ACCOUNT_SID              (set as Basic Auth credential too)
TWILIO_AUTH_TOKEN
TWILIO_FROM_NUMBER              +1XXXXXXXXXX
TWILIO_SMS_FROM                 +1XXXXXXXXXX

DNC_VENDOR_URL                  https://your-dnc-vendor.example.com
DNC_VENDOR_KEY                  (secret)
DNC_VENDOR_NAME                 e.g. 'docusign-dnc'

POSTMARK_TOKEN                  (or SendGrid creds, swap node)
EMAIL_FROM                      reviews@your-domain.com

VM_DROP_URL                     https://vm-drop-vendor.example.com
VM_DROP_KEY                     (secret)

CAL_COM_API_KEY                 (Cal.com API key)
CAL_EVENT_TYPE_ID               1234567

SLACK_WEBHOOK_URL               https://hooks.slack.com/...
```

## Twilio TwiML for the call bridge

The dialer workflow sends `Url=<PUBLIC_BASE_URL>/twiml/medicare-bridge`. Host this minimal TwiML on a Cloudflare Worker / Vercel Function:

```xml
<Response>
  <Say voice="Polly.Joanna">
    Please hold while we connect you with your licensed Medicare agent. We are not Medicare, the federal government, or a Medicare.gov representative. We do not offer every plan available in your area. Currently we represent multiple carriers and offer products in your area. Please contact Medicare dot gov, or 1-800-MEDICARE, or your local SHIP for all your options. This call will be recorded for quality and compliance.
  </Say>
  <Dial record="record-from-answer-dual" recordingStatusCallback="<N8N_BASE_URL>/webhook/twilio-recording" callerId="<TWILIO_FROM_NUMBER>">
    <Number>{{AGENT_PHONE_FOR_AGENT_ID}}</Number>
  </Dial>
</Response>
```

The Worker must look up the agent's phone by `agent_id` from Supabase using the service role key.

## Importing

```
n8n import:workflow --input n8n/01-lead-capture.json
n8n import:workflow --input n8n/02-compliance-gate.json
... (and so on)
```

After import, open each workflow → set credentials (Twilio Basic, Supabase Postgres if you switch from REST) → activate.
