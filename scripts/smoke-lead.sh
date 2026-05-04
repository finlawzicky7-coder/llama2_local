#!/usr/bin/env bash
# scripts/smoke-lead.sh — POST a synthetic lead through the live edge proxy
# with a real HMAC. Use this to drive end-to-end smoke tests.
#
# Required env:
#   PUBLIC_WEB_URL          https://www.your-agency.com
#   SMOKE_PHONE             your own phone number, E.164 (+1XXXXXXXXXX)
#   SMOKE_EMAIL             your own email address
#   SMOKE_STATE             FL/TX/etc.
#   SMOKE_CAMPAIGN_ID       a real campaigns.id from your Supabase
#   SMOKE_TURNSTILE_TOKEN   a valid token (you'll need to grab one from the live page; or set TURNSTILE_BYPASS=1 if your proxy honors a dev bypass)

set -euo pipefail

: "${PUBLIC_WEB_URL:?}"
: "${SMOKE_PHONE:?}"
: "${SMOKE_EMAIL:?}"
: "${SMOKE_STATE:?}"
: "${SMOKE_CAMPAIGN_ID:?}"
: "${SMOKE_TURNSTILE_TOKEN:?}"

payload=$(cat <<JSON
{
  "first_name": "Smoke",
  "last_name": "Test",
  "phone": "$SMOKE_PHONE",
  "email": "$SMOKE_EMAIL",
  "zip_code": "33101",
  "state": "$SMOKE_STATE",
  "medicare_status": "turning_65",
  "current_plan_type": null,
  "desired_help": "Smoke test — do not call",
  "source": "smoke_test",
  "campaign_id": "$SMOKE_CAMPAIGN_ID",
  "landing_page_url": "$PUBLIC_WEB_URL/medicare-review",
  "referrer_url": "",
  "utm_source": "smoke",
  "utm_medium": "smoke",
  "utm_campaign": "smoke",
  "utm_content": "",
  "utm_term": "",
  "consent_given": true,
  "consent_text": "smoke test consent text",
  "consent_version": "tpmo-2026-04-01-v3",
  "consented_entities": [{"name":"Your Agency","role":"TPMO","accepted":true}],
  "tpmo_disclaimer_shown": true,
  "evidence_hash": "smoke",
  "turnstile_token": "$SMOKE_TURNSTILE_TOKEN"
}
JSON
)

echo "POST $PUBLIC_WEB_URL/api/lead-capture"
curl -sS -X POST "$PUBLIC_WEB_URL/api/lead-capture" \
  -H 'content-type: application/json' \
  -d "$payload" | jq .
