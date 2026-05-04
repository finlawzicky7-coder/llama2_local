#!/usr/bin/env bash
# scripts/cleanup-smoke.sh — Remove smoke_test leads + their dependents.
# Use after a smoke test to keep the database clean.
#
# Usage: SUPABASE_DB_URL=postgres://... ./scripts/cleanup-smoke.sh

set -euo pipefail
: "${SUPABASE_DB_URL:?}"

psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
begin;
with smoke as (select id from leads where source = 'smoke_test')
delete from compliance_audit_events where lead_id in (select id from smoke);
delete from recordings where call_log_id in (select id from call_logs where lead_id in (select id from leads where source='smoke_test'));
delete from call_logs where lead_id in (select id from leads where source='smoke_test');
delete from ai_qualification_sessions where lead_id in (select id from leads where source='smoke_test');
delete from appointments where lead_id in (select id from leads where source='smoke_test');
delete from soa_records where lead_id in (select id from leads where source='smoke_test');
delete from enrollments where lead_id in (select id from leads where source='smoke_test');
delete from lead_assignments where lead_id in (select id from leads where source='smoke_test');
delete from dnc_checks where lead_id in (select id from leads where source='smoke_test');
delete from opt_outs where lead_id in (select id from leads where source='smoke_test');
delete from consent_logs where lead_id in (select id from leads where source='smoke_test');
delete from leads where source='smoke_test';
commit;
SQL

echo "Smoke leads removed."
