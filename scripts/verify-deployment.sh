#!/usr/bin/env bash
# scripts/verify-deployment.sh — Pre-flight check before flipping traffic on.
# Exit 0 if every check passes, non-zero otherwise. Each check prints PASS/FAIL.
#
# Required env:
#   SUPABASE_URL                  https://<project>.supabase.co
#   SUPABASE_SERVICE_ROLE_KEY     (secret)
#   N8N_BASE_URL                  https://n8n.your-agency.com
#   PUBLIC_BASE_URL               https://api.your-agency.com
#   PUBLIC_WEB_URL                https://www.your-agency.com
#   WEBHOOK_HMAC_SECRET           (must match Worker + n8n)

set -uo pipefail

fail=0
pass()  { printf "  PASS  %s\n" "$1"; }
fail()  { printf "  FAIL  %s\n" "$1"; fail=1; }
info()  { printf "  INFO  %s\n" "$1"; }
sect()  { printf "\n=== %s ===\n" "$1"; }

require_env() {
  for v in "$@"; do
    if [[ -z "${!v:-}" ]]; then echo "MISSING: $v"; exit 2; fi
  done
}
require_env SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY N8N_BASE_URL PUBLIC_BASE_URL PUBLIC_WEB_URL WEBHOOK_HMAC_SECRET

# ---------------------------------------------------------------------------
sect "Supabase reachability"
code=$(curl -s -o /dev/null -w '%{http_code}' \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "$SUPABASE_URL/rest/v1/leads?select=id&limit=1")
[[ "$code" == "200" ]] && pass "REST reachable" || fail "REST unreachable (HTTP $code)"

# ---------------------------------------------------------------------------
sect "Schema present"
for table in leads consent_logs opt_outs dnc_checks call_logs recordings \
             ai_qualification_sessions appointments lead_assignments \
             soa_records enrollments compliance_audit_events suppression_list \
             campaigns ad_spend agents agent_licenses agent_carrier_appointments; do
  code=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
    "$SUPABASE_URL/rest/v1/$table?select=*&limit=0")
  [[ "$code" == "200" ]] && pass "$table" || fail "$table missing or inaccessible"
done

# ---------------------------------------------------------------------------
sect "Views + functions"
for endpoint in v_lead_reachable v_kpi_daily v_agent_funnel v_compliance_exceptions; do
  code=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
    "$SUPABASE_URL/rest/v1/$endpoint?select=*&limit=0")
  [[ "$code" == "200" ]] && pass "view $endpoint" || fail "view $endpoint missing"
done

# RPC function probes
for fn in fn_score_lead fn_route_lead fn_propagate_opt_out fn_dedupe_lead fn_check_tpmo_consent_integrity; do
  code=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "content-type: application/json" \
    -X POST -d '{}' \
    "$SUPABASE_URL/rest/v1/rpc/$fn")
  # 400 is acceptable here (missing args) — it confirms the function exists.
  [[ "$code" == "200" || "$code" == "400" ]] && pass "rpc $fn" || fail "rpc $fn missing (HTTP $code)"
done

# ---------------------------------------------------------------------------
sect "Storage buckets"
for bucket in call-recordings consent-evidence soa-evidence; do
  code=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    "$SUPABASE_URL/storage/v1/bucket/$bucket")
  [[ "$code" == "200" ]] && pass "bucket $bucket" || fail "bucket $bucket missing (HTTP $code)"
done

# ---------------------------------------------------------------------------
sect "n8n webhooks reachable (1 ping each)"
for path in medicare-lead-capture medicare-compliance-gate medicare-ai-qualify \
            medicare-score-lead medicare-route-lead medicare-dial \
            medicare-followup-cadence medicare-book-appointment medicare-optout; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST \
    -H 'content-type: application/json' \
    -d '{"_probe":true}' \
    "$N8N_BASE_URL/webhook/$path")
  # 200/4xx fine — just want to confirm it's not 502/000 (down).
  if [[ "$code" =~ ^(2|4)[0-9][0-9]$ ]]; then pass "n8n /$path"; else fail "n8n /$path unreachable (HTTP $code)"; fi
done

# ---------------------------------------------------------------------------
sect "Public web + edge"
code=$(curl -s -o /dev/null -w '%{http_code}' "$PUBLIC_WEB_URL/")
[[ "$code" =~ ^2[0-9][0-9]$ ]] && pass "landing page reachable" || fail "landing page HTTP $code"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$PUBLIC_WEB_URL/api/lead-capture")
[[ "$code" =~ ^4[0-9][0-9]$ ]] && pass "lead-capture proxy rejects empty body" || fail "lead-capture proxy unexpected HTTP $code"
code=$(curl -s -o /dev/null -w '%{http_code}' "$PUBLIC_BASE_URL/twiml/medicare-bridge")
[[ "$code" =~ ^2[0-9][0-9]$ ]] && pass "twiml bridge reachable" || fail "twiml bridge HTTP $code"

# ---------------------------------------------------------------------------
sect "TPMO disclaimer present on landing pages (text scan)"
for slug in '' '/medicare-review' '/t65' '/aep'; do
  body=$(curl -sS "$PUBLIC_WEB_URL$slug" || true)
  if grep -qi "do not offer every plan" <<<"$body"; then pass "disclaimer at $slug"; else fail "disclaimer missing at $slug"; fi
  if grep -qi "not affiliated with the federal government\|not Medicare" <<<"$body"; then pass "non-affiliation at $slug"; else fail "non-affiliation missing at $slug"; fi
done

# ---------------------------------------------------------------------------
sect "License coverage for active campaigns"
out=$(curl -sS -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "$SUPABASE_URL/rest/v1/campaigns?active=eq.true&select=id,name")
campaign_count=$(jq -r 'length' <<<"$out")
info "active campaigns: $campaign_count"

agents_with_license=$(curl -sS -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "$SUPABASE_URL/rest/v1/agents?select=id,active,agent_licenses(active)" | jq -r '[.[] | select(.active and (.agent_licenses | map(select(.active)) | length > 0))] | length')
[[ "$agents_with_license" -gt 0 ]] && pass "$agents_with_license active agent(s) with at least one active license" \
                                   || fail "no active agents with active licenses"

# ---------------------------------------------------------------------------
sect "Recent compliance criticals (last 24h)"
crit=$(curl -sS -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "$SUPABASE_URL/rest/v1/compliance_audit_events?severity=eq.critical&created_at=gte.$(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%SZ)&select=id" \
  | jq -r 'length')
[[ "$crit" == "0" ]] && pass "no critical events in last 24h" || fail "$crit critical events in last 24h — investigate"

# ---------------------------------------------------------------------------
echo
if [[ "$fail" -eq 0 ]]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "SOME CHECKS FAILED — do not flip traffic on"
  exit 1
fi
