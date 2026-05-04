#!/usr/bin/env bash
# scripts/setup.sh — Apply Supabase migrations in order. Idempotent.
# Usage: SUPABASE_DB_URL=postgres://... ./scripts/setup.sh

set -euo pipefail

if [[ -z "${SUPABASE_DB_URL:-}" ]]; then
  echo "ERROR: SUPABASE_DB_URL must be set" >&2
  exit 1
fi

cd "$(dirname "$0")/.."

migrations=(
  supabase/migrations/0001_init_core.sql
  supabase/migrations/0002_indexes.sql
  supabase/migrations/0003_rls_policies.sql
  supabase/migrations/0004_views_functions.sql
  supabase/migrations/0005_storage_and_retention.sql
  supabase/migrations/0006_seed.sql
)

for m in "${migrations[@]}"; do
  echo "==> Applying $m"
  psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f "$m"
done

echo
echo "==> Verifying core tables"
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -c "
  select table_name from information_schema.tables
  where table_schema='public'
    and table_name in (
      'agents','agent_licenses','agent_carrier_appointments',
      'leads','consent_logs','opt_outs','dnc_checks',
      'call_logs','recordings','ai_qualification_sessions',
      'appointments','lead_assignments','soa_records','enrollments',
      'compliance_audit_events','suppression_list','campaigns','ad_spend'
    )
  order by 1;
"

echo
echo "==> Verifying RLS is enabled on sensitive tables"
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -c "
  select c.relname, c.relrowsecurity
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
  where n.nspname='public'
    and c.relname in ('leads','consent_logs','call_logs','recordings','compliance_audit_events')
  order by 1;
"

echo
echo "Setup complete."
