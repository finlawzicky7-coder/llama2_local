# Edge Workers (Cloudflare)

Two thin Workers that sit between the public internet and your private services.

## 1. `lead-capture-proxy.ts`

The browser form posts to `www.your-agency.com/api/lead-capture`. This Worker:

1. Verifies the Cloudflare Turnstile token server-side (so the secret never enters the browser).
2. Validates required fields and rejects unsigned/incomplete payloads with structured 4xx errors.
3. Computes an `x-signature` HMAC-SHA256 over the forwarded body using `WEBHOOK_HMAC_SECRET`.
4. Forwards to `https://n8n.your-agency.com/webhook/medicare-lead-capture` with the signature header and the original IP/UA.
5. Returns a stable shape; never leaks upstream errors to the browser.

The Worker exists because **the HMAC secret cannot live in the page**. Without this, anyone could forge a lead.

## 2. `twiml-bridge.ts`

Twilio fetches `api.your-agency.com/twiml/medicare-bridge?agent_id=...&lead_id=...` when an outbound call connects. This Worker:

1. Looks up the agent's phone via Supabase REST with the service-role key (server-only).
2. Returns TwiML that plays the **TPMO disclaimer** and **recording notice** *before* the agent bridges in — so the disclaimer is in the recording even if the agent forgets.
3. Configures dual-channel recording with the recording-completed webhook back to n8n.

This is the layer that mechanically guarantees the "TPMO disclaimer in first 60 s" requirement.

## Deploy

```bash
cd workers
npm i -g wrangler

# Set secrets for the lead-capture proxy
wrangler secret put TURNSTILE_SECRET --env lead_capture
wrangler secret put WEBHOOK_HMAC_SECRET --env lead_capture
wrangler secret put N8N_LEAD_CAPTURE_URL --env lead_capture

wrangler deploy --env lead_capture

# Set secrets for the TwiML bridge
wrangler secret put SUPABASE_URL --env twiml_bridge
wrangler secret put SUPABASE_SERVICE_ROLE_KEY --env twiml_bridge
wrangler secret put TWILIO_FROM_NUMBER --env twiml_bridge
wrangler secret put N8N_RECORDING_WEBHOOK_URL --env twiml_bridge
wrangler secret put AGENCY_NAME --env twiml_bridge
wrangler secret put N_CARRIERS --env twiml_bridge
wrangler secret put N_PLANS --env twiml_bridge

wrangler deploy --env twiml_bridge
```

## Verify

```bash
# Smoke-test the lead-capture proxy with a forged payload (should 403)
curl -sS -X POST https://www.your-agency.com/api/lead-capture \
  -H 'content-type: application/json' \
  -d '{"foo":"bar"}' | jq

# Smoke-test the TwiML bridge with a real agent_id (should return XML)
curl -sS "https://api.your-agency.com/twiml/medicare-bridge?agent_id=$(uuidgen)"
```

## Why a Worker over a Vercel function?

Either works. Cloudflare is recommended because Turnstile + WAF + Pages are already in the same product, and Workers run at the edge with no cold start. If you already use Vercel for the rest of your stack, port these to Vercel functions — the logic transplants in 5 minutes.
